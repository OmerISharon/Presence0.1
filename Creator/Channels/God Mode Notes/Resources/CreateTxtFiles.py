# Directory where the text files will be saved
OUTPUT_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1\\Creator\\God Mode Notes\\Resources\\Text"
import os

# List of 100 uplifting, motivational, encouraging, moving, heartfelt, positive,
# powerful, engaging, exciting, vivid, inspiring, refreshing, hopeful, warm,
# sincere, passionate, creative, brilliant, dynamic, and invigorating quotes.
# The quotes below are taken from popular sources on the internet.
quotes = [
    "The only way to do great work is to love what you do.",
    "Believe you can and you're halfway there.",
    "Your time is limited, so don't waste it living someone else's life.",
    "The best way to predict your future is to create it.",
    "It does not matter how slowly you go as long as you do not stop.",
    "Everything you’ve ever wanted is on the other side of fear.",
    "Dream big and dare to fail.",
    r"You miss 100% of the shots you don't take.",
    "Success is not final, failure is not fatal: It is the courage to continue that counts.",
    "Hardships often prepare ordinary people for an extraordinary destiny.",
    "Believe in yourself and all that you are.",
    "Keep your face always toward the sunshine—and shadows will fall behind you.",
    "The only limit to our realization of tomorrow is our doubts of today.",
    "With the new day comes new strength and new thoughts.",
    "The future belongs to those who believe in the beauty of their dreams.",
    "It always seems impossible until it's done.",
    "What lies behind us and what lies before us are tiny matters compared to what lies within us.",
    "Don't watch the clock; do what it does. Keep going.",
    "Keep your eyes on the stars, and your feet on the ground.",
    "The best way out is always through.",
    "Act as if what you do makes a difference. It does.",
    "Success is not how high you have climbed, but how you make a positive difference to the world.",
    "What you get by achieving your goals is not as important as what you become by achieving your goals.",
    "I can't change the direction of the wind, but I can adjust my sails to always reach my destination.",
    "You are never too old to set another goal or to dream a new dream.",
    "Happiness is not something ready made. It comes from your own actions.",
    "Start where you are. Use what you have. Do what you can.",
    "Don't limit your challenges. Challenge your limits.",
    "If you want to lift yourself up, lift up someone else.",
    "Doubt kills more dreams than failure ever will.",
    "In the middle of every difficulty lies opportunity.",
    "The only person you are destined to become is the person you decide to be.",
    "Go confidently in the direction of your dreams. Live the life you have imagined.",
    "Your life does not get better by chance, it gets better by change.",
    "The secret of getting ahead is getting started.",
    "Believe in the power of your dreams.",
    "Opportunities don't happen, you create them.",
    "Don't be pushed around by the fears in your mind. Be led by the dreams in your heart.",
    "The only way to achieve the impossible is to believe it is possible.",
    "Keep your spirit light, your heart brave, and your mind strong.",
    "Failure is simply the opportunity to begin again, this time more intelligently.",
    "Do something today that your future self will thank you for.",
    "Life is 10% what happens to us and 90% how we react to it.",
    "Strive not to be a success, but rather to be of value.",
    "A journey of a thousand miles begins with a single step.",
    "Your passion is waiting for your courage to catch up.",
    "Magic is believing in yourself, if you can do that, you can make anything happen.",
    "Sometimes the smallest step in the right direction ends up being the biggest step of your life.",
    "Don't wait. The time will never be just right.",
    "Everything you can imagine is real.",
    "Don't be afraid to give up the good to go for the great.",
    "You don't have to be great to start, but you have to start to be great.",
    "Small deeds done are better than great deeds planned.",
    "Do what you can, with what you have, where you are.",
    "Dream as if you'll live forever, live as if you'll die today.",
    "You are braver than you believe, stronger than you seem, and smarter than you think.",
    "Every moment is a fresh beginning.",
    "Turn your wounds into wisdom.",
    "Every day is a chance to change your life.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones.",
    "Dream it. Believe it. Build it.",
    "The harder you work for something, the greater you'll feel when you achieve it.",
    "Don't stop until you're proud.",
    "Wake up with determination. Go to bed with satisfaction.",
    "Make each day your masterpiece.",
    "Sometimes later becomes never. Do it now.",
    "The key to success is to focus on goals, not obstacles.",
    "Dream it, wish it, do it.",
    "Success doesn't just find you. You have to go out and get it.",
    "The future depends on what you do today.",
    "Little by little, a little becomes a lot.",
    "Don't wait for opportunity. Create it.",
    "Difficult roads often lead to beautiful destinations.",
    "Courage is one step ahead of fear.",
    "If you want to achieve greatness stop asking for permission.",
    "Sometimes we’re tested not to show our weaknesses, but to discover our strengths.",
    "If you get tired, learn to rest, not to quit.",
    "Dream big, work hard, stay focused.",
    "Don’t stop when you’re tired. Stop when you’re done.",
    "What seems to us as bitter trials are often blessings in disguise.",
    "If you want to fly, give up everything that weighs you down.",
    "The only thing standing between you and your goal is the story you keep telling yourself.",
    "Perseverance is not a long race; it's many short races one after the other.",
    "No matter how hard the past, you can always begin again.",
    "Never bend your head. Always hold it high. Look the world straight in the eye.",
    "Challenges are what make life interesting and overcoming them is what makes life meaningful.",
    "The best revenge is massive success.",
    "Don't count the days, make the days count.",
    "I am not a product of my circumstances. I am a product of my decisions.",
    "Stay positive, work hard, make it happen.",
    "Life is what we make it, always has been, always will be.",
    "When you feel like quitting, remember why you started.",
    "Life is a journey, and if you fall in love with the journey, you will be in love forever.",
    "Mistakes are proof that you are trying.",
    "Dreams don't work unless you do.",
    "Your only limit is your mind.",
    "Success is the sum of small efforts, repeated day in and day out.",
    "In order to succeed, we must first believe that we can.",
    "Every accomplishment starts with the decision to try."
]

# Define the directory where the quote files will be saved.
# Replace the path below with your specific directory path.
save_path = OUTPUT_DIR

# Create the directory if it doesn't exist.
os.makedirs(save_path, exist_ok=True)

# Save each quote into a separate text file named from 1.txt to 100.txt.
for i, quote in enumerate(quotes, start=1):
    file_name = f"{i}.txt"
    file_path = os.path.join(save_path, file_name)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(quote)

print("100 uplifting quotes have been saved successfully.")
