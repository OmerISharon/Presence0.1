import os

# Directory where the text files will be saved
OUTPUT_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1\\Creator\\God Mode Notes\\Resources\\Text"

# Create the output directory if it does not exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# List of 100 texts (each text is a cohesive message, up to 100 words)
texts = [
"""few are those who see with their own eyes
and feel with their own hearts
most men adopt a new opinion
as they would a new coat""",

"""our lives begin to end the day
we become silent about things that matter
freedom is never voluntarily given
by the oppressor it must be demanded""",

"""cowards die many times before their deaths
the valiant never taste of death but once
of all the wonders that i yet have heard
it seems to me most strange that men should fear""",

"""let us endeavor so to live that
when we come to die even the undertaker
will be sorry
many lack the originality to lack originality""",

"""try not to become a man of success
but rather try to become a man of value
he who dares to waste one hour
of time has not discovered the value of life""",

"""is it not strange that sheep’s guts
should hale souls out of men’s bodies
the price of freedom is eternal vigilance
we must dare to be great""",

"""mankind must put an end to war
before war puts an end to mankind
peace is not the absence of conflict
but the presence of justice""",

"""it is better to die standing
than to live on your knees
the life of man is of no greater duration
than the breath of his nostrils""",

"""a person who never made a mistake
never tried anything new
the important thing is not to stop questioning
curiosity has its own reason for existing""",

"""he who knows others is wise
he who knows himself is enlightened
the wise man does not lay up his own treasures
the more he gives the more he has""",

"""four score and seven years ago
our fathers brought forth on this continent
a new nation conceived in liberty
and dedicated to the proposition that all are equal""",

"""the best way out is always through
happiness is when what you think what you say
and what you do are in harmony
live as if you were to die tomorrow""",

"""don’t wait around for other people
to be happy for you
any happiness you get you’ve got to make yourself
with malice toward none with charity for all""",

"""there is no substitute for victory
it is not enough to fight
it is the spirit which we bring to the fight
that decides the issue""",

"""many of life’s failures are people
who did not realize how close they were
to success when they gave up
opportunity is missed by most because it is dressed in overalls""",

"""the history of the world is
but the biography of great men
every revolution was first a thought
in one man’s mind""",

"""darkness cannot drive out darkness
only light can do that
hate cannot drive out hate
only love can do that""",

"""the life of man is short
he comes forth like a flower
and is cut down like the grass
make haste to live well""",

"""know thyself
the only way to deal with fear
is to face it head on
wisdom begins in wonder""",

"""he that is good with a hammer
thinks everything is a nail
lost time is never found again
diligence is the mother of good luck""",

"""it matters not how strait the gate
how charged with punishments the scroll
i am the master of my fate
i am the captain of my soul""",

"""satisfaction lies in the effort
not in the attainment
full effort is full victory
strength does not come from physical capacity""",

"""this is the short and the long of it
though this be madness yet there is method
in it we know what we are
but know not what we may be""",

"""those who deny freedom to others
deserve it not for themselves
better to remain silent and be thought a fool
than to speak out and remove all doubt""",

"""after climbing a great hill
one only finds that there are many more
hills to climb
resentment is like drinking poison hoping it kills your enemy""",

"""judge not that ye be not judged
for with what judgment ye judge
ye shall be judged
and with what measure ye mete it shall be measured""",

"""men’s evil manners live in brass
their virtues we write in water
the web of our life is of a mingled yarn
good and ill together""",

"""send me the best of your breed
and i will make them better
for i am involved in mankind
no man is an island entire of itself""",

"""there are many paths to the top
of the mountain but the view is always the same
truth never damages a cause that is just
live simply so others may simply live""",

"""i find that the harder i work
the more luck i seem to have
opportunity is missed by most people
because it comes dressed in overalls and looks like work""",

"""your time is limited
so don’t waste it living someone else’s life
don’t be trapped by dogma
which is living with the results of other people’s thinking""",

"""equals should be treated equally
and unequals unequally
give me a lever long enough
and a fulcrum on which to place it""",

"""first they ignore you
then they laugh at you
then they fight you
then you win""",

"""do not wait to strike till
the iron is hot
but make it hot by striking
there is no easy walk to freedom anywhere""",

"""with malice toward none
with charity for all
with firmness in the right
as god gives us to see the right""",

"""for what shall it profit a man
if he shall gain the whole world
and lose his own soul
what is a man advantaged if he lose his own life""",

"""man is born free
and everywhere he is in chains
those who would give up essential liberty
to purchase a little temporary safety deserve neither""",

"""history will be kind to me
for i intend to write it
this is not the end
it is not even the beginning of the end""",

"""although the world is full of suffering
it is also full of the overcoming of it
my optimism does not rest on the absence of evil
but on a glad belief in the preponderance of good""",

"""reading maketh a full man
conference a ready man
and writing an exact man
studies serve for delight for ornament and for ability""",

"""the meaning of life is to find your gift
the purpose of life is to give it away
thousands of candles can be lit
from a single candle and its life will not be shortened""",

"""one swallow does not make a summer
neither does one fine day
similarly one day or brief time of happiness
does not make a person entirely happy""",

"""earth provides enough to satisfy
every man’s needs but not every man’s greed
you must not lose faith in humanity
humanity is an ocean if a few drops are dirty the ocean does not become dirty""",

"""there is no passion to be found
playing small in settling for a life
that is less than the one you are capable of
it seems impossible until it’s done""",

"""the ultimate measure of a man
is not where he stands in moments of comfort
but where he stands at times of challenge
and controversy""",

"""he who has a why to live
can bear almost any how
what is to give light must endure burning
everything can be taken from a man but one thing""",

"""great deeds are usually wrought
at great risks
nothing ventured nothing gained
fortune favors the bold""",

"""tell me and i forget
teach me and i remember
involve me and i learn
an investment in knowledge pays the best interest""",

"""god helps those who help themselves
trust in god but tie your camel
diligence is the mother of good fortune
heaven never helps the man who will not act""",

"""you have power over your mind
not outside events
realize this and you will find strength
very little is needed to make a happy life""",

"""service to others is the rent
you pay for your room here on earth
i am the greatest
i said that even before i knew i was""",

"""yesterday is gone
tomorrow has not yet come
we have only today
let us begin""",

"""energy and persistence conquer all things
he that can have patience can have what he will
lost time is never found again
nothing is so strong as gentleness""",

"""i must not fear
fear is the mind-killer
fear is the little-death
that brings total obliteration""",

"""the time is always right
to do what is right
a right delayed is a right denied
we must keep moving forward""",

"""if i have seen further
it is by standing on the shoulders of giants
we build too many walls
and not enough bridges""",

"""let no man pull you low enough
to hate him
a man who won’t die for something
is not fit to live""",

"""how wonderful it is that nobody
need wait a single moment before starting
to improve the world
act as if what you do makes a difference""",

"""waste no more time arguing
what a good man should be
be one
what you do speaks so loud i cannot hear what you say""",

"""a life spent making mistakes
is not only more honorable
but more useful than a life
spent doing nothing""",

"""people do not lack strength
they lack will
where there’s a will there’s a way
the drop hollows the stone not by force but by falling often""",

"""the best and most beautiful things
in the world cannot be seen or touched
they must be felt with the heart
faith is to believe what you do not see""",

"""my concern is not whether god
is on our side
my greatest concern is to be on god’s side
for god is always right""",

"""no one can make you feel inferior
without your consent
it is our light not our darkness
that most frightens us""",

"""justice delayed is justice denied
the time is always ripe to do right
we must learn to live together
as brothers or perish together as fools""",

"""i’ve failed over and over
and over again in my life
and that is why i succeed
champions keep playing until they get it right""",

"""we must accept finite disappointment
but never lose infinite hope
the moral arc of the universe bends
at the elbow of justice""",

"""if you want to lift yourself up
lift up someone else
i’ve learned that people will forget what you said
but people will never forget how you made them feel""",

"""don’t let yesterday take up
too much of today
the past is a place of reference
not a place of residence""",

"""freedom is never dear at any price
it is the breath of life
what would a man not pay
for living""",

"""you may encounter many defeats
but you must not be defeated
in fact it may be necessary to encounter defeats
so you can know who you are""",

"""there is only one happiness in this life
to love and be loved
love is the only reality
and it is not a mere sentiment""",

"""we delight in the beauty of the butterfly
but rarely admit the changes it has gone through
to achieve that beauty
courage is not the absence of fear but the triumph over it""",

"""good friends good books
and a sleepy conscience
this is the ideal life
many people die with their music still in them""",

"""the price of greatness is responsibility
if you have the ability to see beauty
it’s your duty to share it
we make a living by what we get but a life by what we give""",

"""start by doing what’s necessary
then do what’s possible
and suddenly you are doing the impossible
miracles happen every day if you believe""",

"""i’ve learned that you shouldn’t go through life
with a catcher’s mitt on both hands
you need to be able to throw something back
happiness doesn’t come from what we get but from what we give""",

"""the only person you are destined to become
is the person you decide to be
go confidently in the direction of your dreams
live the life you have imagined""",

"""it is during our darkest moments
that we must focus to see the light
every day brings new choices
hope is passion for what is possible""",

"""children are not things to be molded
but are people to be unfolded
every child is a different kind of flower
and all together make this world a beautiful garden""",

"""happiness is when what you think
what you say and what you do are in harmony
the purpose of our lives is to be happy
peace comes from within do not seek it without""",

"""i am prepared to die
but there is no cause for which
i am prepared to kill
nonviolence is a weapon of the strong""",

"""you must not lose faith in humanity
humanity is an ocean
if a few drops of the ocean are dirty
the ocean does not become dirty""",

"""it’s not the load that breaks you down
it’s the way you carry it
strength does not come from winning
your struggles develop your strengths""",

"""the greatest discovery of all time
is that a person can change his future
by merely changing his attitude
attitude is a little thing that makes a big difference""",

"""nothing in life is to be feared
it is only to be understood
now is the time to understand more
so that we may fear less""",

"""life isn’t about finding yourself
life is about creating yourself
you were born with potential
you were born with goodness and trust""",

"""the whole is greater than
the sum of its parts
alone we can do so little
together we can do so much""",

"""people will forget what you said
people will forget what you did
but people will never forget
how you made them feel""",

"""when one door of happiness closes
another opens but often we look so long
at the closed door that we do not see
the one which has been opened for us""",

"""i would rather die of passion
than of boredom
to dare is to lose one’s footing momentarily
not to dare is to lose oneself""",

"""what lies behind us and what lies
before us are tiny matters compared
to what lies within us
the only way out is through""",

"""you cannot shake hands with a clenched fist
peace is not merely a distant goal
that we seek but a means
by which we arrive at that goal""",

"""success is to be measured not so much
by the position that one has reached in life
as by the obstacles which he has overcome
while trying to succeed"""
]

# Write each text to a separate file named "1.txt", "2.txt", ..., "100.txt"
for index, text in enumerate(texts, start=1):
    file_name = f"{index}.txt"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

print(f"Successfully generated {len(texts)} text files in '{OUTPUT_DIR}'")