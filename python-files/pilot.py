from tkinter import *
from tkinter import messagebox
root = Tk()
root.title('Материалы для подготовки к олимпиаде "Я - профессионал по языкознанию"')
root.geometry('1000x1300')
button_close=Button(root, text="Закрыть", command=quit)
button_close.config(bg='red', fg='black')
button_close.pack()
def next_window():
    root.withdraw()
    second_window = Toplevel(root)
    second_window.protocol("WM_DELETE_WINDOW", root.destroy)
    second_window.title("Задания по русскому языку")
    second_window.geometry('1000x1300')
    #second_window.resizable(True, True)
    canvas=Canvas(second_window)
    frame = Frame(canvas)#, padx=10, pady=10)
    #frame.pack(fill=tk.BOTH, expand=True)
    scrollbar = Scrollbar(second_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")

    canvas.pack(fill="both", expand=True)
    canvas.create_window((0, 0), window=frame, anchor="nw")
    task1 = Label(frame,text="\nКомпетенции в сфере знания паронимов (задание 6 в олимпиаде). В этом разделе 5 заданий. \nОтветы должны вводиться через один пробел без запятых! \nЗадание 1. Редактируя книгу начинающего писателя, вы время от времени исправляете в тексте неправильно употребленные паронимы. Сделайте это в двух следующих предложениях."
"\nВ новом офисе установили акустичную аппаратуру высокого качества, обеспечивающую отличное восприятие речи."
"\nВ ходе судебного разбирательства он представил доказательную базу, подтверждающую его невиновность.")
    task1.pack()
    task1_1 = Entry(frame)
    task1_1.pack()
    def check1():
        if task1_1.get().lower()=='акустическую доказательственную' or task1_1.get().lower()=='акустическая доказательственная':
            messagebox.showinfo("Состояние ответа","Верный ответ")
        elif task1_1.get()=='':
            messagebox.showwarning("Предупреждение", "Введите ответы на задание 1!!")
        else:
            messagebox.showinfo("Состояние ответа", 'Пока неверно. Подумайте ещё!')
    but=Button(second_window, text= 'Проверить задание 1', command=check1)
    but.pack()

    task2 = Label(frame, text="\nЗадание 2.Редактируя книгу начинающего писателя, вы время от времени исправляете в тексте неправильно употребленные паронимы. Сделайте это в двух следующих предложениях."
"\nНа полке стояли книги в кожевных переплетах, изданные в начале XX века."
"\nОн всегда отличался бедствующей на эмоции речью, что создавало впечатление замкнутости.")
    task2.pack()


    task2_2 = Entry(frame)
    task2_2.pack()
    def check2():
        if task2_2.get().lower()=='кожаных бедной' or task2_2.get().lower()=='кожаных бедной':
            messagebox.showinfo("Состояние ответа","Верный ответ")
        elif task2_2.get()=='':
            messagebox.showwarning("Предупреждение", "Введите ответы на задание 2!!")
        else:
            messagebox.showinfo("Состояние ответа", 'Пока неверно. Подумайте ещё!')
    but2 = Button(second_window, text='Проверить задание 2', command=check2)
    but2.pack()
    task3 = Label(frame, text="\nЗадание 3. Редактируя книгу начинающего писателя, вы время от времени исправляете в тексте неправильно употребленные паронимы. Сделайте это в двух следующих предложениях."
"\nВ музее была представлена уникальная историчная реконструкция средневекового города, созданная по архивным материалам."
"\nСтуденты провели экспериментное исследование влияния стресса на когнитивные способности человека.")
    task3.pack()
    task3_1 = Entry(frame)
    task3_1.pack()

    def check3():
        if task3_1.get().lower() == 'историческая экспериментальное':
            messagebox.showinfo("Состояние ответа", "Верный ответ")
        elif task3_1.get() == '':
            messagebox.showwarning("Предупреждение", "Введите ответы на задание 3!!")
        else:
            messagebox.showinfo("Состояние ответа", 'Пока неверно. Подумайте ещё!')

    but4 = Button(second_window, text='Проверить задание 3', command=check3)
    but4.pack()
    task4 = Label(frame, text="\nЗадание 4. Редактируя книгу начинающего писателя, вы время от времени исправляете в тексте неправильно употребленные паронимы. Сделайте это в двух следующих предложениях."
"\nОна купила абонент в бассейн на целый месяц, но посетила всего пару занятий."
"\nМастер с точностью передал анекдотичную ситуацию, но зрители все равно оставались серьезными, не понимая всей комичности сцены.")
    task4.pack()
    task4_1 = Entry(frame)
    task4_1.pack()

    def check4():
        if task4_1.get().lower() == 'абонемент анекдотическую' or task4_1.get().lower() == 'абонемент анекдотическая':
            messagebox.showinfo("Состояние ответа", "Верный ответ")
        elif task4_1.get() == '':
            messagebox.showwarning("Предупреждение", "Введите ответы на задание 4!!")
        else:
            messagebox.showinfo("Состояние ответа", 'Пока неверно. Подумайте ещё!')

    but5 = Button(second_window, text='Проверить задание 4', command=check4)
    but5.pack()
    task5 = Label(frame,
                     text="\nЗадание 5.Редактируя книгу начинающего писателя, вы время от времени исправляете в тексте неправильно употребленные паронимы. Сделайте это в двух следующих предложениях."
"\nЭто был совсем не тот представительный случай, когда можно пойти на риск. Здесь требовалось строгое соблюдение правил."
"\nНовый начальник оказался требовательным, но справедливым: он всегда проводил демонстрационные разборы ошибок, чтобы сотрудники учились на чужих примерах.")
    task5.pack()
    task5_1 = Entry(frame)
    task5_1.pack()

    def check5():
        if task5_1.get().lower() == 'представительский демонстративные':
            messagebox.showinfo("Состояние ответа", "Верный ответ")
        elif task5_1.get() == '':
            messagebox.showwarning("Предупреждение", "Введите ответы на задание 5!!")
        else:
            messagebox.showinfo("Состояние ответа", 'Пока неверно. Подумайте ещё!')

    but6= Button(second_window, text='Проверить задание 5', command=check5)
    but6.pack()
    task11 = Label(frame,
                     text="\nСледующие задания проверяют компетенции в лексикологии и лексическом анализе (задание 1 в реальной олимпиаде). "
                          "\nЗадание 1.Вы проводите учебное занятие, пользуясь методическими разработками старшего коллеги. К сожалению, "
                          "\nколлега не указывает в своих материалах ключи к заданиям (возможно, помнит наизусть или считает тривиальными, а переспросить его невозможно или неудобно). "
                          "\nПо опыту предыдущих примеров вы уверены, что оба слова начинаются на Ж. Восстановите слова-ключи"
                          "\nСо времен «Толкового словаря живого великорусского языка» В. И. Даля некоторые слова частично или полностью изменили свои значения, "
                          "\nдругие полностью или почти полностью исчезли из языка. В значительной степени это касается слов иностранного"
"\nпроисхождения, толкование которых у Даля обычно последовательное и тщательное."
"Какие два слова Даль трактовал так:"
"\n«дневник, поденная записка.., повременное издание.., срочник»."
"\n«Телодвижение человека, немой язык, вольный или невольный; обнаружение знаками,"
"движениями чувств, мыслей»."
"\nКлюч: оба слова начинаются на букву Ж.")
    task11.pack()
    task11_1 = Entry(frame)
    task11_1.pack()

    def check11():
        if task11_1.get().lower() == 'журнал жест':
            messagebox.showinfo("Состояние ответа", "Верный ответ")
        elif task11_1.get() == '':
            messagebox.showwarning("Предупреждение", "Введите ответы на задание 1!!")
        else:
            messagebox.showinfo("Состояние ответа", 'Пока неверно. Подумайте ещё!')

    but7 = Button(second_window, text='Проверить задание 1', command=check11)
    but7.pack()
    task12=Label(frame, text="\nЗадание 2. Угадайте слова по их значению из словаря Даля. Ключ: оба слова начинаются на з"
                                "\n1)наглазный козырек от света, крытый передок в тарантасе"
                                "\n2)остаток по сожжении растений, чего-либо растительного, а иногда и животных веществ")
    task12.pack()
    task12_1 = Entry(frame)
    task12_1.pack()

    def check12():
        if task12_1.get().lower() == 'зонт зола':
            messagebox.showinfo("Состояние ответа", "Верный ответ")
        elif task12_1.get() == '':
            messagebox.showwarning("Предупреждение", "Введите ответы на задание 2!!")
        else:
            messagebox.showinfo("Состояние ответа", 'Пока неверно. Подумайте ещё!')

    task13=Label(frame, text="\nЗадание 3. Угадайте слова по их значению из словаря Даля. Ключ: оба слова начинаются на т"
                    "\n1) дно, испод, основание, как плоскость"
                    "\n2) лошадь, способная перевозить тяжёлые грузы")
    task13.pack()
    task13_1 = Entry(frame)
    task13_1.pack()
    but8 = Button(second_window, text='Проверить задание 2', command=check12)
    but8.pack()
    def check13():
        if task13_1.get().lower() == 'тло тяжеловес':
            messagebox.showinfo("Состояние ответа", "Верный ответ")
        elif task13_1.get() == '':
            messagebox.showwarning("Предупреждение", "Введите ответы на задание 3!!")
        else:
            messagebox.showinfo("Состояние ответа", 'Пока неверно. Подумайте ещё!')

    but9= Button(second_window, text='Проверить задание 3', command=check13)
    but9.pack()

    task14 = Label(frame,
                      text="\nЗадание 4. Угадайте слова по их значению из словаря Даля. Ключ: оба слова начинаются на п"
                           "\n1) пристанище, прибежище, сходбища"
                           "\n2) крыша, кровля, потолок, накат, настилка")
    task14.pack()
    task14_1 = Entry(frame)
    task14_1.pack()

    def check14():
        if task14_1.get().lower() == 'притон палуба':
            messagebox.showinfo("Состояние ответа", "Верный ответ")
        elif task14_1.get() == '':
            messagebox.showwarning("Предупреждение", "Введите ответы на задание 4!!")
        else:
            messagebox.showinfo("Состояние ответа", 'Пока неверно. Подумайте ещё!')

    but10 = Button(second_window, text='Проверить задание 4', command=check14)
    but10.pack()
    def return1():
        root.deiconify()
        second_window.withdraw()
    but3=Button(second_window, text='Домой', command=return1)
    but3.pack()
    frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
bt = Button(root, text="Задания по русскому языку", command=next_window)
bt.pack()
def window3():
    root.withdraw()
    third_window = Toplevel(root)
    third_window.protocol("WM_DELETE_WINDOW", root.destroy)
    third_window.title("Задания по немецкому языку")
    third_window.geometry('1000x1300')
    editor = Text(third_window)
    editor.pack(fill=BOTH, expand=True)
    editor.insert("1.0", "Составитель задач - Марков Даниил\nВопрос  19 (10 баллов)"
                         "\nSie editieren einen deutschen Text. Lesen Sie zuerst den Text und machen Sie anschließend"
                         "Aufgaben nach dem Text:"
                         "\nNetzwerken hat für viele einen negativen Beigeschmack, und es heißt ironisch: „Eine Hand"
                         "wäscht die andere und am Ende sind sie beide dreckig“. Diese Gefahr bestehen immer dann,"
                         "wenn statt der Leistung als Empfehlungskriterium persönliche Interessen im Vordergrund"
                         "stehen: Wenn man also an eine inkompetente Person eine bestimmte Position vergibt, weil"
                         "man sich dadurch für sich selbst einen Nutzen verspricht. Das ist mit Netzwerken nicht"
                         "gemeint. Hier geht es darum, dass man etwa einen Job zwar über Beziehungen, aber aufgrund"
                         "seiner guten Leistung bekommt. Laut einer Untersuchung wurden 2006 34 Prozent der Stellen"
                         "über eigene Mitarbeiter oder persönliche Kontakte besetzt. Gegenwärtig hat schon jeder"
                         "sechste deutsche Großbetrieb ein institutionalisiertes Programm „Mitarbeiter werben"
                         "Mitarbeiter“. Wenn man diese Zahlen liest, ist klar, dass es sich lohnt, Zeit und Mühe in das"
                         "Netzwerken zu investieren."
                         "Jeder Mensch ist bereits – ob er es will oder nicht – Mitglied in mindestens einem Netzwerk,"
                         "nämlich der Familie. Auch die Dorfgemeinschaft stellte in früheren Zeiten ein Netzwerk dar."
                         "Doch funktionieren diese beiden Institutionen nur noch selten im Sinne gegenseitiger"
                         "Unterstützung und Förderung. Deshalb ist es wichtig, sich sein eigenes Netzwerk zu schaffen"
                         "oder Mitglied in einem bestehenden Netzwerk zu werden. Früher gab es im akademischen"
                         "Bereich nur Studentenverbindungen und die standen und stehen bis auf wenige Ausnahmen"
                         "nur männlichen Studenten offen. Heute gibt es jedoch darüber hinaus an einigen deutschen"
                         "Universitäten Alumni-Netzwerke, in denen sich ehemalige Studenten der jeweiligen"
                         "Universität treffen und Kontakte aufbauen."
                         "Darüber hinaus gibt es die traditionellen Netzwerke wie die Rotarier-, Lions- oder KiwanisClubs. Diese haben übrigens Nachwuchsorganisationen, so dass man nicht wohlhabend sein"
                         "und im Leben bereits etwas erreicht haben muss, um Mitglied zu werden. Allerdings braucht"
                         "man immer eine Person – und später zur Aufnahme noch eine zweite –, die dort Mitglied ist"
                         "und einen einlädt. Selbst um die Mitgliedschaft zu bitten, ist meistens nicht möglich."
                         "Besonders beliebt beim Netzwerken sind heute Internetplattformen. Doch wird man auch bei"
                         "Internetnetzwerken feststellen, es geht nichts über den persönlichen Kontakt. Denn die Basis"
                         "des Netzwerkens ist Vertrauen und das lässt sich nur durch persönliches Kennenlernen"
                         "aufbauen."
                         "Vor einigen Jahren gab es eine neue Geschäftsidee: Visitenkartenpartys, eine Plattform, um"
                         "Kontakte herzustellen. Sie ist vor allem für Selbstständige wie Rechtsanwälte oder"
                         "Werbefachleute hilfreich. Auch daraus kann sich an jedem Ort ein Netzwerk entwickeln,"
                         "wenn jemand dazu die Initiative ergreift."
                         "Netzwerke funktionieren dann am besten, wenn sie einen gemeinsamen Zweck verfolgen,"
                         "denn das verbindet. So setzen sich die Kiwanis-Clubs zum Beispiel für das Wohl der Kinder"
                         "ein. Wenn man hier zu offensichtlich seine eigenen Interessen verfolgt, fällt dies negativ auf."
                         "Nicht zuletzt auch deshalb, weil vor dem „Nehmen“ das „Geben“ kommt."
                         "So lässt sich abschließend sagen, um beruflich erfolgreich zu sein, braucht man Kontakte zu"
                         "vielen und natürlich auch zu möglichst einflussreichen Menschen. Bereits das Wort"
                         "„Beförderung“ zeigt, dass man ohne die Unterstützung anderer nicht weit kommt."
                         "\nAufgaben:"
                         "\n1) Formulieren Sie die Hauptidee des Textes in einem Satz (2 Punkte)"
                         "\n2) Finden Sie im Text drei Verben zu verschiedenen Zeiten (Präsens, Präteritum, Perfekt) und erklären, warum der Autor diese Formen verwendet hat (2 Punkte)"
                         "\n3) Finden Sie die unterstrichenen Wörter im Text und zerlegen sie in morphologische Bestandteile (Präfixe, Suffixe usw.) (2 Punkte)"
                         "\n4) Erstellen Sie einen Titel für den Text und erklären Sie im Detail, warum er dazu passt. Der Titel muss mindestens 7 Wörter enthalten (2 Punkte)"
                         "\n5) Finden Sie im ersten Absatz 2 grammatische Fehler (2 Punkte)"
                         "\nInsgesamt max. 10 Punkte"
                         "\nОтвет:"
                         "\n1) Formulieren Sie die Hauptidee des Textes in einem Satz (2 Punkte)"
                         "z. B.: Die Hauptidee des Textes ist, dass Networking, also das Aufbauen und Pflegen von beruflichen Kontakten, für den beruflichen Erfolg unerlässlich ist"
                         "\n2) Finden Sie im Text drei Verben zu verschiedenen Zeiten (Präsens, Präteritum, Perfekt) und erklären, warum der Autor diese Formen verwendet hat (2 Punkte)"
                         "geht (Präsens):  'Hier geht es darum, dass man etwa einen Job zwar über Beziehungen, aber aufgrund seiner guten Leistung bekommt' Grund der Verwendung: Das Präsens wird verwendet, um eine allgemeine Aussage zu machen, die zeitlos gültig ist. Es beschreibt den Kern des positiven Netzwerkens und seine Funktionsweise, unabhängig von einer spezifischen Zeit.."
                         "wurden (Präteritum): 'Laut einer Untersuchung wurden 2006 34 Prozent der Stellen über eigene Mitarbeiter oder persönliche Kontakte besetzt'  Grund der Verwendung: Das Präteritum beschreibt eine abgeschlossene Handlung in der Vergangenheit. Es präsentiert eine statistische Tatsache aus dem Jahr 2006 als konkreten Beleg für die Relevanz von Netzwerken."

                         "haben eingeführt (Perfekt): 'Viele Unternehmen haben bereits  Programme „Mitarbeiter werben Mitarbeiter' eingeführt Hier ist die Handlung des Einführungs der Programme abgeschlossen und liegt in der Vergangenheit.  Die Wirkung (die Programme existieren) ist aber bis in die Gegenwart relevant."

                         "\n3) Finden Sie drei unterstrichene Wörter im Text und zerlegen sie in morphologische Bestandteile (Präfixe, Suffixe usw.) (2 Punkte)"
                         "institutionalisierte: institutionalis-:  Wortstamm, abgeleitet von 'Institution, -iert:  Suffix, Partizip Perfekt (Passiv), zeigt eine abgeschlossene Handlung an und verleiht dem Wort ein adjektivisches Merkmal."
                         "Nachwuchsorganisationen: Nachwuchs-:  Wortstamm (Kompositum aus 'Nachwuchs' und 'Organisationen').  'Nachwuchs' selbst zerlegt sich in: Nach-: Präfix (zeigt Folge oder Bezug auf etwas), wuchs:  Wortstamm (Substantiv, bedeutet 'Wachstum, Entwicklung'; -organisation-: Wortstamm (Substantiv), -en: Suffix (Pluralendung)"
                         "Werbefachleute: werbe-: Wortstamm (Substantiv 'Werbung' im Genitiv), fach-: Wortstamm (Substantiv, bedeutet 'Fachgebiet', 'Spezialisierung'),  -leute: Suffix (Substantivsuffix, bildet zusammengesetzte Substantive, die Personen bezeichnen – 'Leute' ist ein Kollektivum)"

                         "\n4) Erstellen Sie einen Titel für den Text und erklären Sie im Detail, warum er dazu passt. Der Titel muss mindestens 7 Wörter enthalten (2 Punkte)"
                         "Von der Familie zum Online-Netzwerk: Strategien für erfolgreiches Kontaktemanagement. Der Titel umfasst die Bandbreite der im Text beschriebenen Netzwerkformen (Familie, traditionelle Clubs, Online-Plattformen) und betont die strategische Komponente des erfolgreichen Networking."

                         "\n5) Finden Sie im ersten Absatz 2 grammatische Fehler (2 Punkte)"
                         "Netzwerken hat für viele einen negativen Beigeschmack → Netzwerken haben für viele einen negativen Beigeschmack"
                         "Diese Gefahr bestehen immer dann → Diese Gefahr besteht immer dann"
                         "\nВопрос 20 (15 баллов)"

                         "\nSie müssen für den Podkast eines Schauspielers die Beschreibung des Films verfassen,"
                         "dessen kurze Inhaltsangabe unten steht. Ihr Text (min. 150 Wörter) sollte die Zuhörer des"
                         "Podkasts  zum Ansehen des Films motivieren."
                         "Die Beschreibung soll der Film bewerten und das Interesse der Zuschauer wecken. Es muss das Genre des Films, die Zielgruppe bestimmt werden. Ihr Stil sollte der von Ihnen bestimmten Zielgruppe entsprechen."
                         "Ihr Text darf bestimmte Schlüsselwörter aus der Aufgabe aber keine Inhaltsangabe enthalten."
                         "Hier ist nun der Titel und die Inhaltsangabe des Films:"

                         "Friedrich Müller"
                         "Zwölf"

                         "Ein Mordprozess: Ein junger Mann wird beschuldigt, seinen Vater erstochen zu haben. Zwölf Geschworene sollen nun über sein Schicksal entscheiden. Auf den ersten Blick scheint die Sache klar: Die Beweise sind erdrückend, die Zeugenaussagen eindeutig. Elf der Geschworenen sind überzeugt von der Schuld des Angeklagten – nur einer von ihnen nicht."

                         "Doch was als schnelle Abstimmung geplant war, entwickelt sich zu einer hitzigen Debatte. Vorurteile, Emotionen und Zweifel kommen ans Licht, als nach und nach jedes Argument hinterfragt wird. Was bedeutet Gerechtigkeit wirklich? Wie sicher kann sich jemand seiner Meinung sein? Und welche Rolle spielen persönliche Erfahrungen in einer vermeintlich objektiven Entscheidung?"

                         "Die Neuverfilmung des Klassikers 12 Angry Men setzt auf eine moderne Inszenierung und gesellschaftlich relevante Themen. Friedrich Müller übernimmt dabei eine Schlüsselrolle, die das Spannungsverhältnis innerhalb der Gruppe auf neue Weise beleuchtet."

                         "\nInsgesamt max. 15 Punkte"
                         "\nВсего за оба кейса: 25 баллов")
    def return2():
        root.deiconify()
        third_window.withdraw()
    but11=Button(third_window, text='Домой', command=return2)
    but11.pack()
button_n=Button(root, text='Задания по немецкому языку', command=window3)
button_n.pack()
def window4():
    root.withdraw()
    forth_window = Toplevel(root)
    forth_window.protocol("WM_DELETE_WINDOW", root.destroy)
    forth_window.title("Задания по немецкому языку")
    forth_window.geometry('1000x1300')
    editor = Text(forth_window)
    editor.pack(fill=BOTH, expand=True)
    editor.insert("1.0", "Задания по английскому от Антонова Даниила \nАнглийский язык. 20 вопрос – 10 вариантов."
"________________________________________"
"\nВопрос 20 (15 баллов). Var1"
"\nA book description (score points – 15)"
"\nYou need to write a book description for a bookstore website."
"The book is 'To Kill a Mockingbird' by Harper Lee (1960). A plot summary of the book is given below. In your description, evaluate the book to urge the reader to buy it. You should define the genre of the book, the target audience, and tailor the style of your synopsis to the intended audience. You may use some key words from the assignment, but your description should not be reduced to a plot summary of the book (min. 150 words)."
"\nThe plot summary:"
"\nThe novel is set in the American South during the 1930s and follows young Scout Finch as she navigates childhood, learning about justice, morality, and race through the trial of Tom Robinson, a Black man falsely accused of assaulting a white woman. Her father, Atticus Finch, a lawyer, defends Robinson despite facing hostility from the town. The story also explores the mysterious figure of Boo Radley, a reclusive neighbor. Through Scout’s eyes, the reader witnesses the deeply ingrained prejudice in society and the power of empathy and understanding."
"\n________________________________________"
"\nVar2"
"\nA book description (score points – 15)"
"\nYou need to write a book description for a bookstore website."
"\nThe book is '1984' by George Orwell (1949). A plot summary of the book is given below. In your description, evaluate the book to urge the reader to buy it. You should define the genre of the book, the target audience, and tailor the style of your synopsis to the intended audience. You may use some key words from the assignment, but your description should not be reduced to a plot summary of the book (min. 150 words)."
"The plot summary:"
"\nSet in a dystopian future, the novel follows Winston Smith, a citizen of Oceania, where the Party, led by Big Brother, exercises total control over society. Winston secretly despises the Party and begins a rebellious love affair with Julia. However, their defiance is short-lived as they are caught by the Thought Police and subjected to brutal re-education. The novel explores themes of totalitarianism, surveillance, and the fragility of truth in a world where history is constantly rewritten."
"\n________________________________________"
"\nVar3"
"\nA book description (score points – 15)"
"\nYou need to write a book description for a bookstore website."
"\nThe book is 'Pride and Prejudice' by Jane Austen (1813). A plot summary of the book is given below. In your description, evaluate the book to urge the reader to buy it. You should define the genre of the book, the target audience, and tailor the style of your synopsis to the intended audience. You may use some key words from the assignment, but your description should not be reduced to a plot summary of the book (min. 150 words)."
"\nThe plot summary:"
"\nElizabeth Bennet, a witty and independent young woman, meets the seemingly arrogant Mr. Darcy. Despite their initial clashes, their relationship develops through misunderstandings, personal growth, and moments of revelation. Meanwhile, Elizabeth’s family faces various social challenges and romantic entanglements. As Elizabeth learns more about Darcy’s true character, she realizes that first impressions can be misleading. The novel is a timeless exploration of love, class, and self-discovery."
"\n________________________________________"
"\nVar4"
"\nA book description (score points – 15)"
"\nYou need to write a book description for a bookstore website."
"\nThe book is 'Frankenstein' by Mary Shelley (1818). A plot summary of the book is given below. In your description, evaluate the book to urge the reader to buy it. You should define the genre of the book, the target audience, and tailor the style of your synopsis to the intended audience. You may use some key words from the assignment, but your description should not be reduced to a plot summary of the book (min. 150 words)."
"\nThe plot summary:"
"\nVictor Frankenstein, a young scientist, becomes obsessed with creating life. He succeeds in animating a creature from dead body parts, but is horrified by the result and abandons it. The monster, rejected by society, seeks revenge on its creator, leading to a tragic pursuit that spans continents. The novel delves into themes of ambition, responsibility, and the consequences of playing God."
"\n________________________________________"
"\nVar5"
"\nYou need to write a book description for a bookstore website."
"\nThe book is 'The Great Gatsby' by F. Scott Fitzgerald (1925). A plot summary of the book is given below. In your description, evaluate the book to urge the reader to buy it. You should define the genre of the book, the target audience, and tailor the style of your synopsis to the intended audience. You may use some key words from the assignment, but your description should not be reduced to a plot summary of the book (min. 150 words)."
"\nThe plot summary:"
"\nNick Carraway, a young bond salesman, moves to West Egg, where he meets the enigmatic Jay Gatsby, a millionaire known for his lavish parties. Gatsby is in love with Daisy Buchanan, Nick’s cousin, whom he met years ago. As Gatsby rekindles his romance with Daisy, secrets unfold, revealing the hollow nature of wealth and the American Dream. Tragedy follows, leaving Nick disillusioned with the world of privilege and excess."
"\n________________________________________"
"\nVar6"
"\nA book description (score points – 15)"
"\nYou need to write a book description for a bookstore website."
"\nThe book is 'Jane Eyre' by Charlotte Brontë (1847). A plot summary of the book is given below. In your description, evaluate the book to urge the reader to buy it. You should define the genre of the book, the target audience, and tailor the style of your synopsis to the intended audience. You may use some key words from the assignment, but your description should not be reduced to a plot summary of the book (min. 150 words)."
"\nThe plot summary:"
"\nJane Eyre, an orphan raised by a cruel aunt, finds independence as a governess at Thornfield Hall, where she falls in love with the mysterious Mr. Rochester. Their love story is tested when Jane uncovers Rochester’s dark secret—a wife hidden in the attic. Jane chooses self-respect over passion and leaves, only to find love again under different circumstances. The novel explores themes of love, morality, and female independence."
"\n________________________________________"
"\nVar7"
"\nA book description (score points – 15)"
"\nYou need to write a book description for a bookstore website."
"\nThe book is 'Brave New World' by Aldous Huxley (1932). A plot summary of the book is given below. In your description, evaluate the book to urge the reader to buy it. You should define the genre of the book, the target audience, and tailor the style of your synopsis to the intended audience. You may use some key words from the assignment, but your description should not be reduced to a plot summary of the book (min. 150 words)."
"\nThe plot summary:"
"\nIn a technologically advanced future, society is engineered for stability and pleasure, with citizens conditioned to accept their roles. Bernard Marx, an outsider, questions the system and brings back John, a 'Savage' raised outside this world. John struggles with the superficiality of this utopia, leading to tragic consequences. The novel critiques consumerism, control, and the loss of individuality."
"\n________________________________________"
"\nVar8"
"\nA book description (score points – 15)"
"\nYou need to write a book description for a bookstore website."
"\nThe book is 'Crime and Punishment' by Fyodor Dostoevsky (1866). A plot summary of the book is given below. In your description, evaluate the book to urge the reader to buy it. You should define the genre of the book, the target audience, and tailor the style of your synopsis to the intended audience. You may use some key words from the assignment, but your description should not be reduced to a plot summary of the book (min. 150 words)."
"\nThe plot summary:"
"\nRodion Raskolnikov, a destitute student in St. Petersburg, commits murder, believing himself to be above moral law. As guilt consumes him, he faces a psychological and spiritual crisis. Detective Porfiry Petrovich suspects him, while Sonya, a kind-hearted prostitute, urges him to confess. The novel explores redemption, morality, and the torment of a guilty conscience."
"\n________________________________________"
"\nVar9"
"\nA book description (score points – 15)"
"\nYou need to write a book description for a bookstore website."
"\nThe book is 'Moby-Dick' by Herman Melville (1851). A plot summary of the book is given below. In your description, evaluate the book to urge the reader to buy it. You should define the genre of the book, the target audience, and tailor the style of your synopsis to the intended audience. You may use some key words from the assignment, but your description should not be reduced to a plot summary of the book (min. 150 words)."
"\nThe plot summary:"
"\nIshmael, a sailor, joins the whaling ship Pequod, led by the obsessed Captain Ahab, who seeks revenge on Moby Dick, the white whale that took his leg. As the crew ventures into the sea, the pursuit turns into a symbolic struggle between man, nature, and fate. The novel is a deep exploration of obsession, vengeance, and existential questions."
"\n________________________________________"
"\nVar10"
"\nYou need to write a book description for a bookstore website."
"\nThe book is 'Lord of the Flies' by William Golding (1954). A plot summary of the book is given below. In your description, evaluate the book to urge the reader to buy it. You should define the genre of the book, the target audience, and tailor the style of your synopsis to the intended audience. You may use some key words from the assignment, but your description should not be reduced to a plot summary of the book (min. 150 words)."
"\nThe plot summary:"
"\nA group of British schoolboys crash-land on an uninhabited island and attempt to govern themselves. Initially, order prevails, but soon, fear and power struggles lead to chaos. Ralph and Piggy represent civilization, while Jack and his hunters embrace savagery. As morality collapses, the boys descend into violence, revealing the dark nature of humanity. The novel is an allegory of society, leadership, and the fragility of civilization."
"\n________________________________________"
"\nЗадания по английскому от Мохамеда"
"\nVar1"
"\nText 1: The Power of Language"
"\nText:"
"\nLanguage is one of the most powerful tools humans possess. It allows us to communicate complex ideas, share emotions, and build relationships. Through language, we can preserve history, create art, and advance science. However, language is not just a means of communication; it also shapes our thoughts and perceptions. The words we use can influence how we see the world and how others see us. For example, the way we describe events can affect our memory of them. Language is not static; it evolves over time, reflecting changes in society and culture. Understanding the power of language is essential for effective communication and critical thinking."
"\nQuestions:"
"\n1) What is one of the most powerful tools humans possess?"
"\n2)How does language shape our thoughts and perceptions?"
"\n3) What can the way we describe events affect?"
"\n4) How does language evolve over time?"
"\n5) Why is understanding the power of language important?"
"\nAnswers:"
"\n1) Language is one of the most powerful tools humans possess."
"\n2) Language shapes our thoughts and perceptions by influencing how we see the world."
"\n3) The way we describe events can affect our memory of them."
"\n4) Language evolves over time, reflecting changes in society and culture."
"\n5) Understanding the power of language is essential for effective communication and critical thinking."

"\nText 2: The Role of Technology in Education"
"\nText:"
"\nTechnology has revolutionized the field of education. With the advent of computers, the internet, and mobile devices, students now have access to a wealth of information at their fingertips. Online learning platforms and educational apps have made it possible for people to learn at their own pace and from anywhere in the world. However, the integration of technology in education also presents challenges. Not all students have equal access to digital resources, and there is a risk of over-reliance on technology, which can hinder critical thinking and problem-solving skills. Despite these challenges, technology has the potential to make education more inclusive and personalized."
"\nQuestions:"
"\n1) How has technology revolutionized education?"
"\n2) What have online learning platforms and educational apps made possible?"
"\n3) What are two challenges of integrating technology in education?"
"\n4) What is a potential risk of over-reliance on technology?"
"\n5) What potential does technology have in education?"
"\nAnswers:"
"\n1) Technology has revolutionized education by providing access to a wealth of information and new learning tools."
"\n2) Online learning platforms and educational apps have made it possible for people to learn at their own pace and from anywhere in the world."
"\n3) Challenges include unequal access to digital resources and the risk of over-reliance on technology."
"\n4) Over-reliance on technology can hinder critical thinking and problem-solving skills."
"\n5) Technology has the potential to make education more inclusive and personalized."
"\nText 3: The Importance of Biodiversity"
"\nText:"
"\nBiodiversity refers to the variety of life on Earth, including all species of plants, animals, and microorganisms. It is essential for the health of ecosystems and the survival of humanity. Biodiversity provides us with food, medicine, and raw materials. It also plays a crucial role in regulating the climate, purifying water, and pollinating crops. However, biodiversity is under threat due to human activities such as deforestation, pollution, and climate change. The loss of biodiversity can have severe consequences, including the collapse of ecosystems and the loss of vital resources. Protecting biodiversity is therefore a global priority."
"\nQuestions:"
"\n1) What does biodiversity refer to?"
"\n2) Why is biodiversity essential for humanity?"
"\n3) What are three benefits of biodiversity?"
"\n4) What are two threats to biodiversity?"
"\n5) Why is protecting biodiversity a global priority?"
"\nAnswers:"
"\n1) Biodiversity refers to the variety of life on Earth, including all species of plants, animals, and microorganisms."
"\n2) Biodiversity is essential for the health of ecosystems and the survival of humanity."
"\n3) Biodiversity provides food, medicine, and raw materials, regulates the climate, purifies water, and pollinates crops."
"\nThreats to biodiversity include deforestation, pollution, and climate change."
"\nProtecting biodiversity is a global priority because its loss can lead to the collapse of ecosystems and the loss of vital resources."
"\nText 4: The Role of Art in Society"
"\nText:"
"\nArt has always played a significant role in society, serving as a medium for expression, communication, and reflection. It allows individuals and communities to convey their emotions, beliefs, and experiences. Art can also challenge societal norms and provoke thought, leading to social change. Throughout history, art has been used to document events, celebrate cultural heritage, and inspire innovation. Despite its importance, art is often undervalued in modern society, with funding for the arts frequently being cut. Recognizing the value of art is essential for fostering creativity and preserving cultural identity."
"\nQuestions:"
"\n1) What role does art play in society"
"\n2) How can art lead to social change?"
"\n3) What are three historical uses of art?"
"\n4) What is a current challenge facing the arts?"
"\n5) Why is recognizing the value of art important?"
"\nAnswers:"
"\n1) Art serves as a medium for expression, communication, and reflection."
"\n2) Art can challenge societal norms and provoke thought, leading to social change."
"\n3) Art has been used to document events, celebrate cultural heritage, and inspire innovation."
"\n4) A current challenge is the frequent cutting of funding for the arts."
"\n5) Recognizing the value of art is important for fostering creativity and preserving cultural identity."

"\nText 5: The Evolution of Human Rights"
"\nText:"
"\nThe concept of human rights has evolved over centuries. Initially, rights were often tied to social status and privilege. The Enlightenment era marked a turning point, with philosophers advocating for the inherent rights of all individuals. The Universal Declaration of Human Rights, adopted by the United Nations in 1948, established a global standard for human rights. Despite this progress, human rights violations persist in many parts of the world. Issues such as discrimination, inequality, and political oppression continue to challenge the realization of universal human rights. The fight for human rights is ongoing and requires global cooperation and vigilance."
"\nQuestions:"
"\n1) How has the concept of human rights evolved?"
"\n2) What marked a turning point in the concept of human rights?"
"\n3) What did the Universal Declaration of Human Rights establish?"
"\n4) What are two ongoing challenges to human rights?"
"\n5) What is required to fight for human rights?"
"\nAnswers:"
"\n1) The concept of human rights has evolved from being tied to social status to being recognized as inherent to all individuals."
"\n2) The Enlightenment era marked a turning point in the concept of human rights."
"\nThe Universal Declaration of Human Rights established a global standard for human rights."
"\nOngoing challenges include discrimination, inequality, and political oppression."
"\nThe fight for human rights requires global cooperation and vigilance."

"\nText 6: The Impact of Globalization"
"\nText:"
"\nGlobalization refers to the increasing interconnectedness of the world's economies, cultures, and populations. It has been driven by advances in technology, transportation, and communication. Globalization has led to the spread of ideas, goods, and services across borders, fostering economic growth and cultural exchange. However, it has also resulted in challenges such as economic inequality, cultural homogenization, and environmental degradation. The benefits and drawbacks of globalization are complex and multifaceted, requiring careful consideration and management to ensure that its positive aspects are maximized while minimizing its negative impacts."
"\nQuestions:"
"\nWhat does globalization refer to?"
"\nWhat has driven globalization?"
"\nWhat are two positive effects of globalization?"
"\nWhat are two challenges associated with globalization?"
"\nWhat is required to manage the impacts of globalization?"
"\nAnswers:"
"\nGlobalization refers to the increasing interconnectedness of the world's economies, cultures, and populations."
"\nGlobalization has been driven by advances in technology, transportation, and communication."
"\nPositive effects include economic growth and cultural exchange."
"\nChallenges include economic inequality, cultural homogenization, and environmental degradation."
"\nManaging the impacts of globalization requires careful consideration to maximize benefits and minimize negative impacts."
"\nText 7: The Future of Artificial Intelligence"
"\nText:"
"\nArtificial intelligence (AI) is rapidly transforming various aspects of society, from healthcare and education to transportation and entertainment. AI systems can analyze vast amounts of data, make predictions, and perform tasks that were once thought to require human intelligence. While AI has the potential to improve efficiency and solve complex problems, it also raises ethical concerns. Issues such as job displacement, privacy, and bias in AI algorithms need to be addressed. The future of AI will depend on how society navigates these challenges and ensures that AI is developed and used responsibly."
"\nQuestions:"
"\nWhat is artificial intelligence transforming?"
"\nWhat can AI systems do?"
"\nWhat are two potential benefits of AI?"
"\nWhat are two ethical concerns related to AI?"
"\nWhat will the future of AI depend on?"
"\nAnswers:"
"\nAI is transforming healthcare, education, transportation, and entertainment."
"\nAI systems can analyze data, make predictions, and perform complex tasks."
"\nPotential benefits include improved efficiency and solving complex problems."
"\nEthical concerns include job displacement, privacy, and bias in AI algorithms."
"\nThe future of AI will depend on how society addresses challenges and ensures responsible development and use.")
    def return3():
        root.deiconify()
        forth_window.withdraw()
    but12=Button(forth_window, text='Домой', command=return3)
    but12.pack()
button_e = Button(root, text='Задания по английскому языку', command=window4)
#button_e.config(bg='pink', fg='blue')
button_e.pack()
root.mainloop()