class MBTIQuiz:
    def __init__(self):
        self.questions = {
            "E/I": [
                ("I prefer social gatherings over staying alone.", "E"),
                ("I get energized by spending time alone.", "I"),
                ("I enjoy sharing ideas with many people.", "E"),
                ("I prefer deep one-on-one conversations.", "I")
            ],
            "S/N": [
                ("I trust facts and experience more than theories.", "S"),
                ("I like abstract ideas and possibilities.", "N"),
                ("I focus on the details rather than the big picture.", "S"),
                ("I often think about future possibilities and innovation.", "N")
            ],
            "T/F": [
                ("I make decisions based on logic rather than emotions.", "T"),
                ("I prioritize people's feelings when making decisions.", "F"),
                ("I value fairness over personal considerations.", "T"),
                ("I am empathetic and care about how decisions affect people.", "F")
            ],
            "J/P": [
                ("I prefer a planned and organized lifestyle.", "J"),
                ("I am flexible and adapt as things change.", "P"),
                ("I like setting schedules and sticking to them.", "J"),
                ("I prefer going with the flow rather than planning everything.", "P")
            ]
        }
        self.scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

    def ask_questions(self):
        print("Answer with 'yes' or 'no':")
        for category, qs in self.questions.items():
            for question, type_ in qs:
                answer = input(f"{question} (yes/no): ").strip().lower()
                if answer == "yes":
                    self.scores[type_] += 1

    def calculate_type(self):
        type_ = ""
        type_ += "E" if self.scores["E"] > self.scores["I"] else "I"
        type_ += "S" if self.scores["S"] > self.scores["N"] else "N"
        type_ += "T" if self.scores["T"] > self.scores["F"] else "F"
        type_ += "J" if self.scores["J"] > self.scores["P"] else "P"
        return type_

    def start(self):
        print("Welcome to the MBTI Quiz Game!")
        self.ask_questions()
        result = self.calculate_type()
        print(f"Your Myers-Briggs personality type is: {result}")

if __name__ == "__main__":
    quiz = MBTIQuiz()
    quiz.start()
