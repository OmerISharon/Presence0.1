"""
vector_manager.py
~~~~~~~~~~~~~~~~~~~~~
A small utility module for embedding text **and** images into a shared
vector space (OpenAI CLIP) and finding the nearest match.

Dependencies
------------
pip install sentence-transformers pillow numpy torch   # torch >= 2.0 recommended

Example
-------
from vector_manager import CrossModalVector, CrossModalItem, most_similar

cmv   = CrossModalVector()                       # loads the CLIP model once
query = cmv.embed_text("A sleepy golden retriever")
bank  = [
    CrossModalItem("dog.png",  cmv.embed_image("dog.png")),
    CrossModalItem("car.jpg",  cmv.embed_image("car.jpg")),
    CrossModalItem("cat.jpeg", cmv.embed_image("cat.jpeg")),
]

best = most_similar(query, bank)                 # returns the best-matching item
print(best.ref)                                  # -> dog.png
"""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterable, List, Sequence, Union

import numpy as np
from PIL import Image
import requests
from sentence_transformers import SentenceTransformer, util


@dataclass(frozen=True, slots=True)
class CrossModalItem:
    """A wrapper that couples any reference (str | Path | metadata) with its embedding."""
    ref: Union[str, Path, object]
    vector: np.ndarray  # 1-D, already L2-normalised


class CrossModalVector:
    """
    Encapsulates a CLIP model so it is loaded only once and shared safely
    across threads / processes (torch’s lazy init + Python’s module cache).
    """

    _DEFAULT_MODEL = "clip-ViT-B-32"

    def __init__(self, model_name: str | None = None, *, device: str | None = None):
        self.model = SentenceTransformer(model_name or self._DEFAULT_MODEL, device=device)
        self.model.max_seq_length = 77  # CLIP default

    # ------------------------------------------------------------------ embed
    def embed_text(self, text: Union[str, Sequence[str]]) -> np.ndarray:
        """Return L2-normalised CLIP embedding(s) for a string or sequence."""
        return self._encode(text, is_image=False)

    def embed_image(
        self, img: Union[str, Path, Image.Image, Sequence[Union[str, Path, Image.Image]]]
    ) -> np.ndarray:
        """Return L2-normalised CLIP embedding(s) for an image or sequence."""
        return self._encode(img, is_image=True)

    # ---------------------------------------------------------------- helpers
    def _encode(
        self,
        data: Union[str, Path, Image.Image, Sequence[Union[str, Path, Image.Image]]],
        *,
        is_image: bool,
        batch_size: int = 32,
        convert_to_numpy: bool = True,
        normalise_embeddings: bool = True,
    ) -> np.ndarray:
        if isinstance(data, (str, Path, Image.Image)):
            data = [data]  # type: ignore[arg-type]

        # If needed, load image paths into PIL.Image
        if is_image:
            data = [Image.open(d).convert("RGB") if not isinstance(d, Image.Image) else d for d in data]  # type: ignore[arg-type]

        embeddings = self.model.encode(
            list(data), batch_size=batch_size, convert_to_numpy=convert_to_numpy, normalize_embeddings=normalise_embeddings
        )
        return embeddings if len(embeddings.shape) > 1 else embeddings.reshape(1, -1)
    

    # ---------------------------------------------------------------- lookup
    def similarity(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Cosine similarity (vectorised) using sentence-transformers util for speed."""
        return util.cos_sim(a, b)  # returns torch / np; small overhead OK


# ================================================================ retrieval
def most_similar(
    query: np.ndarray,
    items: Iterable[CrossModalItem],
    *,
    top_k: int = 1,
) -> Union[CrossModalItem, List[CrossModalItem]]:
    """
    Return the single best item (default) or a list of the *k* best items.

    *Assumes* every CrossModalItem.vector is **already unit-normalised**.
    """
    bank_vectors = np.stack([it.vector for it in items], dtype=np.float32)  # (n, d)
    sims = (bank_vectors @ query.squeeze().T).squeeze()  # cosine because unit-norm

    if top_k == 1:
        idx = int(np.argmax(sims))
        return list(items)[idx]

    top_idx = np.argpartition(-sims, top_k - 1)[:top_k]
    ranked = sorted(((i, sims[i]) for i in top_idx), key=lambda t: -t[1])
    ordered_items = [list(items)[i] for i, _ in ranked]
    return ordered_items


def load_image_from_url(url: str) -> Image.Image:
    """Download and return an image from a web URL as a PIL.Image."""
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGB")


def find_best_image_for_text(text_context: str, image_paths: list[str]) -> str:
    """
    Efficiently finds the best matching image (local or URL) to the given text.
    Uses batching for faster embedding.
    """
    cmv = CrossModalVector()
    query_vector = cmv.embed_text(text_context)[0]

    images = []
    refs = []

    # Load all images or paths in one pass
    for path in image_paths:
        if path.startswith("http://") or path.startswith("https://"):
            try:
                image = load_image_from_url(path)
                images.append(image)
                refs.append(path)
            except Exception as e:
                print(f"⚠️ Failed to load {path}: {e}")
        else:
            images.append(path)
            refs.append(path)

    if not images:
        return "[ERROR] No valid images"

    # 🔥 Batch embed all at once
    vectors = cmv.embed_image(images)

    # Pair refs with vectors
    items = [
        CrossModalItem(ref, vector)
        for ref, vector in zip(refs, vectors)
    ]

    best_match = most_similar(query_vector, items)
    return str(best_match.ref)


# def find_best_image_for_text(text_context: str, image_paths: list[str]) -> str:
#     """
#     Given a text context and a list of image file paths or URLs,
#     returns the path or URL of the image most similar to the text context.

#     Args:
#         text_context: A descriptive text string.
#         image_paths: List of image file paths or web URLs.

#     Returns:
#         The file path or URL of the best matching image.
#     """
#     cmv = CrossModalVector()
#     query_vector = cmv.embed_text(text_context)[0]

#     items = []
#     for path in image_paths:
#         if path.startswith("http://") or path.startswith("https://"):
#             image = load_image_from_url(path)
#             vector = cmv.embed_image(image)[0]
#         else:
#             vector = cmv.embed_image(path)[0]

#         items.append(CrossModalItem(path, vector))

#     best_match = most_similar(query_vector, items)
#     return str(best_match.ref)


# DEMO RUN

def main():
    """
    Demo test:
    1. Hardcoded deep text description.
    2. Hardcoded list of 5 image paths (update these paths to actual files).
    3. Returns best matching image path for the text.
    """
    print("Starting vector manager demo run...")

    # Example deep text
    deep_text = (
        # "A majestic snow-covered mountain under a clear blue sky with pine trees at its base."
        "A lonely flower"
    )

    # Example image paths (replace with real paths on your system)
    image_paths = [
        fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules\utilities\vector_manager\test_images\pexels-sebastian-palomino-933481-1955134.jpg",
        fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules\utilities\vector_manager\test_images\pexels-jmark-250591.jpg",
        # fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules\utilities\vector_manager\test_images\pexels-soldiervip-1386604.jpg",
        # fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules\utilities\vector_manager\test_images\pexels-pawelkalisinski-1076758.jpg",
        fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules\utilities\vector_manager\test_images\pexels-jonaskakaroto-736230.jpg",
        fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules\utilities\vector_manager\test_images\pexels-stijn-dijkstra-1306815-3265460.jpg"
    ]
    

    cmv = CrossModalVector()
    query_vector = cmv.embed_text(deep_text)[0]  # single vector

    items = [
        CrossModalItem(path, cmv.embed_image(path)[0])
        for path in image_paths
    ]

    best_match = most_similar(query_vector, items)
    print(f"Best matching image: {best_match.ref}")

if __name__ == "__main__":
    main()
