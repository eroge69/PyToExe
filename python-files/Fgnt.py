import sys
import math
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QLineEdit, QStackedWidget, QComboBox, 
                            QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QIntValidator, QRegularExpressionValidator

class PrimeChecker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        title = QLabel("بررسی عدد اول")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        description = QLabel("یک عدد طبیعی وارد کنید (بزرگتر از 1):")
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)
        
        self.numberInput = QLineEdit()
        self.numberInput.setAlignment(Qt.AlignCenter)
        self.numberInput.setValidator(QIntValidator(0, 999999999, self))
        layout.addWidget(self.numberInput)
        
        checkButton = QPushButton("بررسی")
        checkButton.clicked.connect(self.checkNumber)
        layout.addWidget(checkButton)
        
        self.resultLabel = QLabel()
        self.resultLabel.setAlignment(Qt.AlignRight)
        self.resultLabel.setWordWrap(True)
        self.resultLabel.setMargin(10)
        layout.addWidget(self.resultLabel)
        
        self.setLayout(layout)

    def checkNumber(self):
        text = self.numberInput.text()
        ok, n = text.isdigit(), int(text) if text.isdigit() else 0
        
        if not ok:
            self.resultLabel.setText("لطفاً یک عدد معتبر وارد کنید.")
            self.resultLabel.setStyleSheet("background-color: #f8d7da; color: #721c24;")
            return
        
        if n < 0:
            self.resultLabel.setText("عدد وارد شده منفی است. لطفاً یک عدد طبیعی وارد کنید.")
            self.resultLabel.setStyleSheet("background-color: #f8d7da; color: #721c24;")
            return

        if n == 0:
            self.resultLabel.setText("0 جز اعداد طبیعی نیست.")
            self.resultLabel.setStyleSheet("background-color: #fcf8e3; color: #8a6d3b;")
        elif n == 1:
            self.resultLabel.setText("عدد 1 نه اول است نه مرکب.")
            self.resultLabel.setStyleSheet("background-color: #fcf8e3; color: #8a6d3b;")
        else:
            if self.isPrime(n):
                self.resultLabel.setText(f"{n} عدد اول است.")
                self.resultLabel.setStyleSheet("background-color: #dff0d8; color: #3c763d;")
            else:
                divisors = []
                for i in range(2, n):
                    if n % i == 0:
                        divisors.append(str(i))
                self.resultLabel.setText(f"{n} عدد مرکب است و بر اعداد زیر بخش پذیر است:\n{', '.join(divisors)}")
                self.resultLabel.setStyleSheet("background-color: #f2dede; color: #a94442;")

    def isPrime(self, n):
        if n <= 1:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True

class TermInput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        
        self.signSelect = QComboBox()
        self.signSelect.addItem("+")
        self.signSelect.addItem("-")
        layout.addWidget(self.signSelect)
        
        self.termInput = QLineEdit()
        self.termInput.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.termInput)
        
        self.setLayout(layout)
    
    def getTerm(self):
        return self.termInput.text()
    
    def getSign(self):
        return self.signSelect.currentText()
    
    def setTerm(self, term):
        self.termInput.setText(term)
    
    def setSign(self, sign):
        self.signSelect.setCurrentText(sign)

class UnionCalculator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.termCount = 2
        self.termInputs = []
        
        mainLayout = QVBoxLayout(self)
        
        title = QLabel("محاسبه‌گر اتحادهای جبری")
        title.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(title)
        
        typeLayout = QHBoxLayout()
        typeLabel = QLabel("نوع اتحاد:")
        self.unionType = QComboBox()
        self.unionType.addItem("مربع دو جمله‌ای (a±b)²")
        self.unionType.addItem("اتحاد مزدوج (a+b)(a-b)")
        self.unionType.addItem("اتحاد جمله مشترک (x+a)(x+b)")
        self.unionType.addItem("مربع سه جمله‌ای (a+b+c)²")
        self.unionType.addItem("سفارشی (چند جمله‌ای)")
        self.unionType.currentIndexChanged.connect(self.onUnionTypeChanged)
        
        typeLayout.addWidget(typeLabel)
        typeLayout.addWidget(self.unionType)
        mainLayout.addLayout(typeLayout)
        
        self.controlsLayout = QHBoxLayout()
        self.addTermButton = QPushButton("اضافه کردن جمله")
        self.removeTermButton = QPushButton("حذف جمله")
        self.addTermButton.clicked.connect(self.addTerm)
        self.removeTermButton.clicked.connect(self.removeTerm)
        
        self.controlsLayout.addWidget(self.addTermButton)
        self.controlsLayout.addWidget(self.removeTermButton)
        mainLayout.addLayout(self.controlsLayout)
        
        self.termsContainer = QWidget()
        self.termsLayout = QVBoxLayout(self.termsContainer)
        mainLayout.addWidget(self.termsContainer)
        
        self.calculateButton = QPushButton("محاسبه اتحاد")
        self.calculateButton.clicked.connect(self.calculate)
        mainLayout.addWidget(self.calculateButton)
        
        self.errorLabel = QLabel()
        self.errorLabel.setStyleSheet("color: #721c24;")
        self.errorLabel.setAlignment(Qt.AlignCenter)
        self.errorLabel.hide()
        mainLayout.addWidget(self.errorLabel)
        
        self.resultLabel = QLabel()
        self.resultLabel.setAlignment(Qt.AlignRight)
        self.resultLabel.setWordWrap(True)
        self.resultLabel.setMargin(10)
        self.resultLabel.hide()
        mainLayout.addWidget(self.resultLabel)
        
        # Add initial terms
        for _ in range(2):
            self.addTerm()
        
        self.setLayout(mainLayout)
        self.onUnionTypeChanged(0)  # Initialize for first type

    def onUnionTypeChanged(self, index):
        if index == 4:  # Custom
            self.controlsLayout.setEnabled(True)
        else:
            self.controlsLayout.setEnabled(False)
            self.resetTermsForType(index)
    
    def addTerm(self):
        if self.termCount >= 6:
            self.showError("حداکثر 6 جمله قابل اضافه کردن است")
            return
        
        newTerm = TermInput()
        self.termsLayout.addWidget(newTerm)
        self.termInputs.append(newTerm)
        self.termCount += 1
        self.clearError()
    
    def removeTerm(self):
        if self.termCount <= 2:
            self.showError("حداقل 2 جمله باید وجود داشته باشد")
            return
        
        lastTerm = self.termsLayout.itemAt(self.termsLayout.count() - 1).widget()
        self.termsLayout.removeWidget(lastTerm)
        self.termInputs.pop()
        lastTerm.deleteLater()
        self.termCount -= 1
        self.clearError()
    
    def calculate(self):
        self.clearError()
        self.hideResult()
        
        terms = []
        signs = []
        
        for termInput in self.termInputs:
            term = termInput.getTerm().strip()
            sign = termInput.getSign()
            
            if not term:
                self.showError("لطفاً همه عبارات را پر کنید")
                return
            
            regex = QRegularExpression("^[a-zA-Z0-9.*+\\- /^()]*$")
            if not regex.match(term).hasMatch():
                self.showError("فقط حروف انگلیسی، اعداد و نمادهای ریاضی مجاز هستند")
                return
            
            terms.append(term)
            signs.append(sign)
        
        try:
            expression = ""
            expanded = ""
            
            # Build expression
            for i in range(self.termCount):
                if i > 0:
                    expression += " " + signs[i] + " "
                elif signs[i] == "-":
                    expression += "-"
                expression += terms[i]
            
            type_ = self.unionType.currentIndex()
            
            if type_ == 0:  # Square (a±b)²
                a = terms[0]
                b = terms[1]
                sign = signs[1]
                
                expanded = f"{a}² {'+' if sign == '+' else '-'} 2{'' if sign == '+' else '-'}{a}{b} + {b}²"
                self.resultLabel.setText(f"({expression})² = {expanded}")
            elif type_ == 1:  # Conjugate (a+b)(a-b)
                a = terms[0]
                b = terms[1]
                
                expanded = f"{a}² - {b}²"
                self.resultLabel.setText(f"({a} + {b})({a} - {b}) = {expanded}")
            elif type_ == 2:  # Common (x+a)(x+b)
                x = terms[0]
                a = terms[1]
                b = terms[2]
                
                expanded = f"{x}² + ({a} + {b}){x} + {a}.{b}"
                self.resultLabel.setText(f"({x} + {a})({x} + {b}) = {expanded}")
            elif type_ == 3:  # Triple (a+b+c)²
                a = terms[0]
                b = terms[1]
                c = terms[2]
                
                expanded = f"{a}² + {b}² + {c}² + 2{a}{b} + 2{a}{c} + 2{b}{c}"
                self.resultLabel.setText(f"({a} + {b} + {c})² = {expanded}")
            else:  # Custom
                expanded = self.expandCustomPolynomial(terms, signs)
                self.resultLabel.setText(f"({expression})² = {expanded}")
            
            self.showResult()
        except Exception as e:
            self.showError(f"خطا در محاسبه: {str(e)}")

    def resetTermsForType(self, type_):
        # Remove extra terms
        while self.termCount > 2:
            self.removeTerm()
        
        # Add terms if needed for specific types
        if type_ == 2 or type_ == 3:  # Common or Triple
            self.addTerm()
        
        # Set default values
        if type_ == 0:  # Square
            self.termInputs[0].setTerm("a")
            self.termInputs[1].setTerm("b")
            self.termInputs[0].setSign("+")
            self.termInputs[1].setSign("+")
        elif type_ == 1:  # Conjugate
            self.termInputs[0].setTerm("a")
            self.termInputs[1].setTerm("b")
            self.termInputs[0].setSign("+")
            self.termInputs[1].setSign("-")
        elif type_ == 2:  # Common
            self.termInputs[0].setTerm("x")
            self.termInputs[1].setTerm("a")
            self.termInputs[2].setTerm("b")
            self.termInputs[0].setSign("+")
            self.termInputs[1].setSign("+")
            self.termInputs[2].setSign("+")
        elif type_ == 3:  # Triple
            self.termInputs[0].setTerm("a")
            self.termInputs[1].setTerm("b")
            self.termInputs[2].setTerm("c")
            self.termInputs[0].setSign("+")
            self.termInputs[1].setSign("+")
            self.termInputs[2].setSign("+")
    
    def expandCustomPolynomial(self, terms, signs):
        squaredTerms = []
        crossTerms = []
        
        for i in range(len(terms)):
            squaredTerms.append(f"{terms[i]}²")
            
            for j in range(i + 1, len(terms)):
                sign = "+" if signs[i] == signs[j] else "-"
                crossTerms.append(f"2{sign}{terms[i]}{terms[j]}")
        
        return " + ".join(squaredTerms) + " " + " ".join(crossTerms)
    
    def showError(self, message):
        self.errorLabel.setText(message)
        self.errorLabel.show()
    
    def clearError(self):
        self.errorLabel.clear()
        self.errorLabel.hide()
    
    def showResult(self):
        self.resultLabel.show()
    
    def hideResult(self):
        self.resultLabel.clear()
        self.resultLabel.hide()

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("برنامه ریاضی")
        self.setStyleSheet("font-family: Arial; font-size: 9px;")
        
        mainLayout = QVBoxLayout(self)
        
        # Header
        header = QLabel()
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("border-bottom: 1px solid #ddd; padding-bottom: 7px;")
        mainLayout.addWidget(header)
        
        # Navigation
        navLayout = QHBoxLayout()
        primeButton = QPushButton("اعداد اول")
        unionButton = QPushButton("اتحادهای جبری")
        
        navLayout.addWidget(primeButton)
        navLayout.addWidget(unionButton)
        mainLayout.addLayout(navLayout)
        
        # Stacked Widget for pages
        self.stackedWidget = QStackedWidget()
        
        primePage = PrimeChecker()
        unionPage = UnionCalculator()
        
        self.stackedWidget.addWidget(primePage)
        self.stackedWidget.addWidget(unionPage)
        mainLayout.addWidget(self.stackedWidget)
        
        # Footer
        footer = QLabel("تهیه شده توسط یونس شهریاری")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size: 8px; color: #666; border-top: 1px solid #ddd; padding-top: 7px;")
        mainLayout.addWidget(footer)
        
        # Connect navigation buttons
        primeButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        unionButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        
        self.setLayout(mainLayout)
        self.resize(560, 600)

def main():
    app = QApplication(sys.argv)
    
    # Set RTL layout direction
    app.setLayoutDirection(Qt.RightToLeft)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()