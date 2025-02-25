import os

# Directory where the text files will be saved.
OUTPUT_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1\\Creator\\RedNBlack\\Resources\\Text"

# Create the output directory if it does not exist.
os.makedirs(OUTPUT_DIR, exist_ok=True)

# List of 100 texts (each text is a cohesive message with delay markers)
texts = [
    """The most beautiful things in life [1]
cannot be seen, only felt [1]
deep inside your heart [1]""",
    
    """Forget the past [2]
no one becomes successful by living there [2]""",
    
    """Learn from yesterday [1]
live for today [1]
hope for tomorrow [1]""",
    
    """Life is really simple [1]
but we make it hard with our own thoughts [1]""",
    
    """A journey of a thousand miles [1]
begins with a single step [1]""",
    
    """Be kind to those around you [1]
for kindness opens many doors [1]""",
    
    """Respect your elders [1]
their words are full of quiet wisdom [1]""",
    
    """Take time to enjoy a quiet moment [1]
it refreshes your tired soul [1]""",
    
    """Listen to the soft voice within [1]
it tells you the truth of your heart [1]""",
    
    """Work hard for your dreams [1]
but never forget to rest [1]""",
    
    """Your heart holds the key to joy [1]
unlock it with simple acts of love [1]""",
    
    """Do not fear failure [1]
each mistake teaches you a lesson [1]""",
    
    """Hold your head high [1]
and walk with a steady heart [1]""",
    
    """Patience is the friend of success [1]
let time reveal your true worth [1]""",
    
    """Every day is a new beginning [1]
embrace it with a hopeful mind [1]""",
    
    """Remember the warmth of a mother's love [1]
it is a light that never fades [1]""",
    
    """Honor your father's guidance [1]
carry his wisdom in your steps [1]""",
    
    """Take care of your inner self [1]
for it is the source of all strength [1]""",
    
    """Face your fears with courage [1]
and you will find true freedom [1]""",
    
    """Let sorrow teach you compassion [1]
and pain guide you to growth [1]""",
    
    """Keep your words gentle [1]
they can mend a broken heart [1]""",
    
    """Hold onto hope in dark times [1]
it is the spark that lights your way [1]""",
    
    """Be true to yourself [1]
even when the road is hard [1]""",
    
    """Embrace change with an open heart [1]
it brings new chances to shine [1]""",
    
    """Let love be your constant guide [1]
and truth be your firm foundation [1]""",
    
    """Small steps lead to big changes [1]
start today with a clear mind [1]""",
    
    """Keep your life simple [1]
and your heart will remain pure [1]""",
    
    """Take time to reflect on your journey [1]
learn from every twist and turn [1]""",
    
    """Gratitude turns what you have into enough [1]
speak thanks with every breath [1]""",
    
    """Hold fast to your dreams [1]
and never let doubt overshadow them [1]""",
    
    """Let each sunrise remind you [1]
that hope is reborn every day [1]""",
    
    """Trust in the path you walk [1]
even when it is shrouded in mist [1]""",
    
    """Be brave in the face of challenge [1]
for courage is born in struggle [1]""",
    
    """Quiet moments bring deep thoughts [1]
and clear the clutter of the mind [1]""",
    
    """Speak with honesty and listen with care [1]
for truth binds all great hearts [1]""",
    
    """Remember that time heals all wounds [1]
patience is a friend in sorrow [1]""",
    
    """Let your actions speak louder than words [1]
they reveal the truth of your spirit [1]""",
    
    """Be gentle with yourself [1]
and forgive your own mistakes [1]""",
    
    """Life is a book [1]
each day writes a new page [1]""",
    
    """Dream big but stay grounded [1]
for reality and hope must blend [1]""",
    
    """Every heart has its story [1]
let yours be one of quiet strength [1]""",
    
    """Show love to those who need it [1]
a simple act can change a life [1]""",
    
    """Let your smile be a light [1]
in the darkest corners of the world [1]""",
    
    """Stand firm in your beliefs [1]
and let your soul be your guide [1]""",
    
    """Sometimes silence speaks the loudest [1]
listen to what it has to say [1]""",
    
    """Take time to appreciate the little things [1]
they build the foundation of a happy life [1]""",
    
    """Share your wisdom with the young [1]
for they are the future of our dreams [1]""",
    
    """Be thankful for both joy and pain [1]
each teaches you a valuable lesson [1]""",
    
    """Let the past be a lesson [1]
and the future a canvas of hope [1]""",
    
    """Trust that you are enough [1]
and the world will see your light [1]""",
    
    """Hold on to the truth in your heart [1]
it will guide you through stormy times [1]""",
    
    """Every struggle is a chance to grow [1]
embrace it with a willing spirit [1]""",
    
    """Keep your dreams close [1]
and work steadily to make them real [1]""",
    
    """Honor the love you have known [1]
and let it strengthen you each day [1]""",
    
    """Life is a journey of simple steps [1]
take each one with care and joy [1]""",
    
    """Remember that hard times pass [1]
and brighter days will come [1]""",
    
    """Let your heart be full of grace [1]
and your mind free of fear [1]""",
    
    """Keep your focus on what matters [1]
and let distractions fade away [1]""",
    
    """Find beauty in every moment [1]
and let your spirit be uplifted [1]""",
    
    """Take a deep breath and move forward [1]
one step at a time is enough [1]""",
    
    """Be mindful of the power of a kind word [1]
it can heal more than you know [1]""",
    
    """Stay humble in times of success [1]
and gracious in moments of loss [1]""",
    
    """Let each day bring a fresh start [1]
and every night a time to reflect [1]""",
    
    """Hold your head high with quiet pride [1]
and let your heart remain gentle [1]""",
    
    """Keep love as your guiding star [1]
and truth as your constant companion [1]""",
    
    """Sometimes a simple prayer is enough [1]
to lift the weight of your worries [1]""",
    
    """Listen to the lessons of the past [1]
but do not dwell in sorrow [1]""",
    
    """Each day is a gift of chance [1]
open it with gratitude and care [1]""",
    
    """Walk your path with steady purpose [1]
and let your actions show your strength [1]""",
    
    """May your heart be full of hope [1]
and your mind free of doubt [1]""",
    
    """Let each moment of struggle [1]
be a stepping stone to wisdom [1]""",
    
    """Remember that you are never alone [1]
kindness lives in every gentle act [1]""",
    
    """Be mindful of the beauty of life [1]
even in the smallest of things [1]""",
    
    """Allow yourself to feel every emotion [1]
for they make you deeply human [1]""",
    
    """Keep your spirit open and your heart kind [1]
life will reward your gentle ways [1]""",
    
    """Be patient with your own progress [1]
growth comes in quiet moments [1]""",
    
    """Let the simple truth guide you [1]
and wisdom will follow your steps [1]""",
    
    """Trust that every day has its own purpose [1]
and every night brings peace [1]""",
    
    """Find strength in the warmth of home [1]
and love in the eyes of family [1]""",
    
    """Be aware of the power of your thoughts [1]
they shape the path you walk [1]""",
    
    """Keep the light of hope burning [1]
even when the road is dark [1]""",
    
    """Let your journey be one of quiet courage [1]
and simple acts of kindness [1]""",
    
    """Stand firm in the face of life’s trials [1]
and let each challenge build your character [1]""",
    
    """Take comfort in the gentle rhythm of time [1]
each moment brings its own healing [1]""",
    
    """Let the peace of nature fill your soul [1]
and the sound of life calm your mind [1]""",
    
    """Remember that every ending is a start [1]
and every loss a chance to begin anew [1]""",
    
    """Embrace the quiet moments with care [1]
they are the seeds of future joy [1]""",
    
    """Live with a heart that is open [1]
and a mind that seeks truth [1]""",
    
    """May you always find a reason to smile [1]
even in the simplest of days [1]""",
    
    """Let your actions be filled with gentle strength [1]
and your words with honest hope [1]""",
    
    """Keep your soul light with grateful thoughts [1]
and your steps sure on the path of life [1]""",
    
    """Every breath is a new beginning [1]
and every moment a chance to shine [1]""",
    
    """Remember the lessons learned from each fall [1]
and rise with renewed purpose [1]""",
    
    """Let your heart listen to the quiet truth [1]
and your mind find peace in simple things [1]""",
    
    """Embrace your past with a forgiving heart [1]
and look to the future with clear hope [1]""",
    
    """May you find strength in every small victory [1]
and comfort in every shared smile [1]""",
    
    """Live with sincerity and a gentle spirit [1]
for these are the marks of true wisdom [1]""",
    
    """Let each day be a step towards a better you [1]
and every night a time to rest and dream [1]""",
    
    """Be brave, be kind, and stay true [1]
for these simple truths will guide you [1]""",
    
    """May your life be filled with quiet grace [1]
and your journey marked by gentle triumphs [1]"""
]

# Write each text to a separate file named "1.txt", "2.txt", ..., "100.txt".
for index, text in enumerate(texts, start=1):
    file_name = f"{index}.txt"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

print(f"Successfully generated {len(texts)} text files in '{OUTPUT_DIR}'")
