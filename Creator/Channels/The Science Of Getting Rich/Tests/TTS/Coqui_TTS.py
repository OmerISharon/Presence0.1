from TTS.api import TTS  # Coqui TTS
import os

# Variables
text = "Hey, I'm your speaker model. do you like my voice bro? Thanks!"
output_dir = "D:\\2025\\Projects\\Presence\\Presence0.1\\Creator\\The Science Of Getting Rich\\Tests\\TTS\\Output_Dir"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Initialize the TTS model. Adjust progress_bar and gpu as needed.
tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=True, gpu=False)

# Manually defined list of speakers (only the speaker names)
speakers = [
    "p225", "p226", "p227", "p228", "p229", "p230", "p231", "p232", "p233", "p234",
    "p236", "p237", "p238", "p239", "p240", "p241", "p243", "p244", "p245", "p246",
    "p247", "p248", "p249", "p250", "p251", "p252", "p253", "p254", "p255", "p256",
    "p257", "p258", "p259", "p260", "p261", "p262", "p263", "p264", "p265", "p266",
    "p267", "p268", "p269", "p270", "p271", "p272", "p273", "p274", "p275", "p276",
    "p277", "p278", "p279", "p280", "p281", "p282", "p283", "p284", "p285", "p286",
    "p287", "p288", "p292", "p293", "p294", "p295", "p297", "p298", "p299", "p300",
    "p301", "p302", "p303", "p304", "p305", "p306", "p307", "p308", "p310", "p311",
    "p312", "p313", "p314", "p316", "p317", "p318", "p323", "p326", "p329", "p330",
    "p333", "p334", "p335", "p336", "p339", "p340", "p341", "p343", "p345", "p347",
    "p351", "p360", "p361", "p362", "p363", "p364", "p374", "p376", "p377", "p378",
    "p379", "p380", "p381", "p382", "p383", "p384", "p385", "p386", "p387", "p388",
    "p389", "p390", "p391", "p392", "p393", "p394", "p395", "p396", "p397", "p398",
    "p399", "p400", "p401", "p402", "p403", "p404", "p405", "p406", "p407", "p408",
    "p409", "p410", "p411", "p412", "p413", "p414", "p415", "p416", "p417", "p418",
    "p419", "p420", "p421", "p422", "p423", "p424", "p425", "p426", "p427", "p428",
    "p429", "p430", "p431", "p432", "p433", "p434"
]

# Loop over each speaker and synthesize the text.
for speaker in speakers:
    # Remove any extra whitespace or newline characters from the speaker string
    speaker_clean = speaker.strip()

    # Build the output file path; file name will be the cleaned speaker name (e.g., "p225.wav").
    output_path = os.path.join(output_dir, f"{speaker_clean}.wav")
    
    print(f"Generating audio for speaker {speaker_clean} -> {output_path}")
    
    # Synthesize and save the audio file for the given speaker.
    tts.tts_to_file(text=text, speaker=speaker_clean, file_path=output_path)
