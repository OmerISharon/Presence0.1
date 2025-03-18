import os

# Directory where the text files will be saved
OUTPUT_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1\\Creator\\RedNBlack\\Resources\\Text"

# Create the output directory if it does not exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# List of 100 texts (each text is a cohesive message with delay markers)
texts = [
"""be yourself everyone else is taken [1]
many lack originality of lacking originality [2]
most people are other people [3]""",

"""i have a dream [1]
faith is taking the first step [2]
we shall overcome [3]""",

"""to be or not to be [1]
all the world’s a stage [2]
brevity is the soul of wit [3]""",

"""the only thing we have to fear [1]
is fear itself [2]
when you reach the end of your rope [3]""",

"""imagination is more important than knowledge [1]
in the middle of difficulty lies opportunity [2]
strive not to be a success but [3]""",

"""give me liberty or give me death [1]
i know not what course others may take [2]
is life so dear or peace so sweet [3]""",

"""ask not what your country can do [1]
for you but what you can do [2]
for your country [3]""",

"""i think therefore i am [1]
the heart has its reasons [2]
doubt is the origin of wisdom [3]""",

"""in the middle of difficulty lies opportunity [1]
anyone who has never made a mistake [2]
has never tried anything new [3]""",

"""the journey of a thousand miles [1]
begins with one step [2]
when the wind blows build walls [3]""",

"""all men are created equal [1]
government of the people by the people [2]
a house divided against itself cannot stand [3]""",

"""an eye for an eye makes [1]
the whole world blind [2]
where there is love there is life [3]""",

"""life is what you make it [1]
whatever you are be a good one [2]
the best way to predict the future [3]""",

"""i came i saw i conquered [1]
divide and rule [2]
fortune favors the bold [3]""",

"""genius is one percent inspiration [1]
ninety-nine percent perspiration [2]
i have not failed just found [3]""",

"""let them eat cake [1]
after us the deluge [2]
i was born at versailles [3]""",

"""we shall overcome [1]
injustice anywhere is a threat to justice [2]
i have a dream that one day [3]""",

"""carpe diem seize the day [1]
you may delay but time will not [2]
nothing is ours except time [3]""",

"""the unexamined life is not worth living [1]
i know nothing except my ignorance [2]
the only true wisdom is knowing [3]""",

"""time is money [1]
early to bed early to rise [2]
an investment in knowledge pays the best [3]""",

"""i am the master of my fate [1]
i am the captain of my soul [2]
out of the night that covers me [3]""",

"""where there is love there is life [1]
we must be the change we wish [2]
an eye for an eye makes [3]""",

"""to thine own self be true [1]
this above all else [2]
neither a borrower nor a lender be [3]""",

"""the best way to predict the future [1]
is to create it [2]
whatever you are be a good one [3]""",

"""education is the most powerful weapon [1]
it always seems impossible until it’s done [2]
the greatest glory in living lies [3]""",

"""do unto others as you would have [1]
the truth will set you free [2]
love your neighbor as yourself [3]""",

"""a room without books is like [1]
a body without a soul [2]
the life of man is short [3]""",

"""no man is an island [1]
any man’s death diminishes me [2]
ask not for whom the bell tolls [3]""",

"""we must be the change we wish [1]
the weak can never forgive forgiveness [2]
freedom is not worth having if [3]""",

"""i have not failed just found [1]
ten thousand ways that won’t work [2]
genius is one percent inspiration [3]""",

"""the only way to do great work [1]
is to love what you do [2]
stay hungry stay foolish [3]""",

"""give me a place to stand [1]
and i will move the earth [2]
necessity is the mother of invention [3]""",

"""freedom is not worth having if [1]
it does not include freedom to err [2]
truth is powerful and will prevail [3]""",

"""it always seems impossible until it’s done [1]
the greatest glory in living lies [2]
education is the most powerful weapon [3]""",

"""whatever you are be a good one [1]
i walk slowly but i never [2]
life is what you make it [3]""",

"""the truth will set you free [1]
blessed are the peacemakers [2]
love your enemies and pray [3]""",

"""i disapprove of what you say [1]
but defend your right to say it [2]
man is born free [3]""",

"""success is not final failure not fatal [1]
never give in never give in [2]
we shall fight on the beaches [3]""",

"""life is either a daring adventure [1]
or nothing at all [2]
keep your face to the sunshine [3]""",

"""knowledge is power [1]
truth is the daughter of time [2]
experience is the teacher of all [3]""",

"""happiness is not something readymade [1]
it comes from your own actions [2]
be kind whenever possible [3]""",

"""i know nothing except my ignorance [1]
the unexamined life is not worth living [2]
one thing only i know [3]""",

"""you must be the change you wish [1]
an eye for an eye makes [2]
the best way out is always through [3]""",

"""the greatest glory in living lies [1]
not in never falling but rising [2]
it always seems impossible until it’s done [3]""",

"""when you reach the end of your rope [1]
tie a knot and hang on [2]
the only thing we have to fear [3]""",

"""a journey of a thousand miles [1]
begins with a single step [2]
the way is not in the sky [3]""",

"""i am not afraid of storms [1]
for i am learning to sail [2]
little women grow up strong [3]""",

"""do what you can with what you have [1]
where you are [2]
believe you can and you’re halfway there [3]""",

"""there is no path to happiness [1]
happiness is the path [2]
the mind is everything what you think [3]""",

"""the pen is mightier than the sword [1]
words are sharper than blades [2]
truth cuts deeper than steel [3]""",

"""i have a dream that one day [1]
every valley shall be exalted [2]
we shall overcome [3]""",

"""float like a butterfly sting like a bee [1]
don’t count the days make them count [2]
impossible is just an opinion [3]""",

"""it is never too late to be [1]
what you might have been [2]
the past is a stepping stone [3]""",

"""we are what we repeatedly do [1]
excellence then is not an act [2]
but a habit [3]""",

"""be the change you wish to see [1]
in the world [2]
an eye for an eye blinds all [3]""",

"""what does not kill me makes me stronger [1]
that which is hateful to you [2]
do not impose on others [3]""",

"""the future belongs to those who believe [1]
in the beauty of their dreams [2]
do one thing every day that scares [3]""",

"""love your neighbor as yourself [1]
blessed are the meek [2]
the kingdom of heaven is within [3]""",

"""a man who stands for nothing [1]
will fall for anything [2]
truth has no agenda [3]""",

"""i walk slowly but i never [1]
walk backward [2]
whatever you are be a good one [3]""",

"""if you can dream it you can [1]
do it [2]
all our dreams can come true [3]""",

"""turn your wounds into wisdom [1]
you get what you give [2]
the big lesson in life is never [3]""",

"""the mind is everything what you think [1]
you become [2]
there is no path to happiness [3]""",

"""injustice anywhere is a threat to justice [1]
everywhere [2]
i have a dream that one day [3]""",

"""you miss one hundred percent of shots [1]
you don’t take [2]
aim high even if you miss [3]""",

"""i am because we are [1]
forgiveness is not an occasional act [2]
truth and love will always triumph [3]""",

"""do one thing every day that scares [1]
you [2]
the future belongs to those who believe [3]""",

"""the only limit to our realization [1]
is our doubts of today [2]
when you reach the end of your rope [3]""",

"""peace begins with a smile [1]
spread love everywhere you go [2]
if you judge people you have no [3]""",

"""i will prepare and someday my chance [1]
will come [2]
whatever you are be a good one [3]""",

"""we are all in the gutter [1]
but some look at the stars [2]
be yourself everyone else is taken [3]""",

"""life is really simple but we insist [1]
on making it complicated [2]
the wise man knows his limits [3]""",

"""the best revenge is massive success [1]
living well is the best revenge [2]
success is the sweetest victory [3]""",

"""if you judge people you have no [1]
time to love them [2]
peace begins with a smile [3]""",

"""strive not to be a success but [1]
rather to be of value [2]
imagination is more important than knowledge [3]""",

"""you only live once but if you [1]
do it right once is enough [2]
life is short make it count [3]""",

"""to live is the rarest thing [1]
in the world most people exist [2]
we are all in the gutter [3]""",

"""i refuse to accept despair as final [1]
we shall overcome [2]
faith is taking the first step [3]""",

"""there is nothing permanent except change [1]
the only constant is change [2]
adapt or fade away [3]""",

"""the greatest wealth is to live content [1]
with little [2]
wisdom is better than gold [3]""",

"""spread love everywhere you go [1]
peace begins with a smile [2]
if you judge people you have no [3]""",

"""believe you can and you’re halfway there [1]
do what you can with what you have [2]
the only limit to our realization [3]""",

"""it’s not whether you get knocked down [1]
it’s whether you get up [2]
keep going no matter what [3]""",

"""the only true wisdom is knowing [1]
you know nothing [2]
i know nothing except my ignorance [3]""",

"""let us sacrifice our today so that [1]
our children can have tomorrow [2]
it always seems impossible until it’s done [3]""",

"""everything you’ve ever wanted is on [1]
the other side of fear [2]
fear is the mind-killer [3]""",

"""i alone cannot change the world [1]
but i can cast a stone [2]
spread love everywhere you go [3]""",

"""don’t judge each day by the harvest [1]
but by seeds you plant [2]
small acts grow big futures [3]""",

"""what we think we become [1]
the mind is everything [2]
happiness is the path [3]""",

"""success is going from failure to failure [1]
without losing enthusiasm [2]
never give in never give in [3]""",

"""the weak can never forgive forgiveness [1]
is the attribute of the strong [2]
we must be the change we wish [3]""",

"""you can’t blame gravity for falling [1]
in love [2]
love is a force of nature [3]""",

"""keep your face to the sunshine [1]
and you cannot see a shadow [2]
life is either a daring adventure [3]""",

"""never give in never give in [1]
never never never [2]
success is not final failure not fatal [3]""",

"""not everything that counts can be counted [1]
imagination is more important than knowledge [2]
strive not to be a success but [3]""",

"""hate cannot drive out hate only love [1]
can do that [2]
i have a dream that one day [3]""",

"""do what is right not what is easy [1]
the truth will set you free [2]
stand firm in your own light [3]""",

"""life is 10 percent what happens [1]
90 percent how you react [2]
you control your own destiny [3]"""
]

# Write each text to a separate file named "1.txt", "2.txt", ..., "100.txt"
for index, text in enumerate(texts, start=1):
    file_name = f"{index}.txt"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

print(f"Successfully generated {len(texts)} text files in '{OUTPUT_DIR}'")