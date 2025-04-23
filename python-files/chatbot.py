import time

class RadiographyTutor:
    def __init__(self):
        self.topics = {
            "1": {
                "title": "X-ray Production",
                "explanation": (
                    "X-rays are produced when high-energy electrons collide with a metal target, "
                    "typically tungsten. This occurs in an X-ray tube through three main processes: "
                    "bremsstrahlung radiation, characteristic radiation, and electron cascade."
                ),
                "questions": [
                    {
                        "question": "What are the main components of an X-ray tube?",
                        "keywords": ["cathode", "anode", "vacuum", "glass envelope", "filament"],
                        "answer": (
                            "Main components include:\n"
                            "- Cathode (filament electron source)\n"
                            "- Rotating anode (tungsten target)\n"
                            "- Vacuum-sealed glass envelope\n"
                            "- High voltage potential between electrodes"
                        )
                    },
                    {
                        "question": "What's the difference between bremsstrahlung and characteristic radiation?",
                        "keywords": ["bremsstrahlung", "deceleration", "characteristic", "shell", "electron"],
                        "answer": (
                            "Bremsstrahlung (braking radiation) occurs when electrons decelerate near atomic nuclei, "
                            "producing a continuous spectrum. Characteristic radiation results from electron "
                            "transitions between atomic shells, producing specific energy peaks."
                        )
                    }
                ]
            },
            "2": {
                "title": "Image Contrast",
                "explanation": (
                    "Radiographic contrast refers to the difference in density between adjacent areas on an image. "
                    "It depends on subject contrast (object properties) and detector contrast. "
                    "Key factors include tissue density, atomic number, and thickness."
                ),
                "questions": [
                    {
                        "question": "How does kVp affect image contrast?",
                        "keywords": ["higher kVp", "lower contrast", "penetration", "scatter"],
                        "answer": (
                            "Higher kVp:\n"
                            "- Increases photon penetration\n"
                            "- Reduces contrast (more shades of gray)\n"
                            "- Increases scatter radiation\n"
                            "Lower kVp enhances contrast but may require higher mAs"
                        )
                    }
                ]
            }
        }

    def start(self):
        print("Welcome to Radiography Tutor using Feynman Technique!\n")
        while True:
            self.show_topics()
            choice = input("\nChoose a topic number or 'q' to quit: ")
            if choice.lower() == 'q':
                break
            self.teach_topic(choice)

    def show_topics(self):
        print("\nAvailable Topics:")
        for num, topic in self.topics.items():
            print(f"{num}. {topic['title']}")

    def teach_topic(self, choice):
        topic = self.topics.get(choice)
        if not topic:
            print("Invalid selection. Please try again.")
            return

        print(f"\n→ Topic: {topic['title']}\n")
        print("Step 1: Concept Explanation")
        print(f"\n{topic['explanation']}\n")
        input("Press Enter when you're ready to explain the concept in your own words...")

        while True:
            user_explanation = input("\nExplain the concept in your own words (or type 'help' for hints):\n")
            if user_explanation.lower() == 'help':
                print(f"\nHint: Focus on these elements:\n{topic['explanation']}")
                continue
            break

        print("\nStep 2: Identify Knowledge Gaps")
        self.ask_questions(topic['questions'])

        print("\nStep 3: Review and Simplify")
        print("\nLet's review the key points:")
        print(topic['explanation'])
        print("\nTry simplifying your explanation further:")
        time.sleep(2)
        print("\nExample simple explanation:")
        print(f"{topic['explanation'].split('.')[0]} - Think of it like [...]")

    def ask_questions(self, questions):
        score = 0
        for i, q in enumerate(questions, 1):
            print(f"\nQuestion {i}: {q['question']}")
            answer = input("Your answer: ").lower()
            if any(keyword in answer for keyword in q['keywords']):
                print(f"\n✅ Good! You mentioned important concepts.")
                score += 1
            else:
                print(f"\n❌ Missed some key points. Let's review:")
                print(f"\nComplete Answer:\n{q['answer']}")
            time.sleep(1)
        
        print(f"\nScore: {score}/{len(questions)}")
        if score == len(questions):
            print("Excellent understanding!")
        else:
            print("Review the material and try explaining again later.")

if __name__ == "__main__":
    tutor = RadiographyTutor()
    tutor.start()
    print("\nThank you for using Radiography Tutor! Keep practicing!")