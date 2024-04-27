import locale

from kivy.config import Config


Config.set('graphics', 'width', '540')
Config.set('graphics', 'height', '800')


from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from datetime import date, datetime
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang.builder import Builder
from kivy.uix.scrollview import ScrollView
from database import DataBase
import sqlite3
from kivy.uix.widget import Widget

Builder.load_file("financas.kv")
cadastro = ObjectProperty()
gastocategoria = ObjectProperty()
gastodata = ObjectProperty()
gastodescricao = ObjectProperty()
gastovalor = ObjectProperty()





# =============== CLASSES E PÁGINAS =================


conn = sqlite3.connect('gastos.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS tabela_gastos (data DATE, categoria, 
    descricao, valor REAL)''')
c.close()
conn.commit()

# =========================== PRINCIPAL
class PaginaPrincipal(Screen, FloatLayout):

    with open('cadastro.txt', 'r') as arquivo:
        linhas = arquivo.readlines()
    categorias = [linha.strip() for linha in linhas]
    print(categorias)

    def incluir_gasto(self):
        data_string = self.gastodata.text.replace('/','-')
        data_obj = datetime.strptime(data_string, '%d-%m-%Y')
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        valor_em_reais = locale.currency(float(self.gastovalor.text), grouping=True)
        conn = sqlite3.connect('gastos.db')
        c = conn.cursor()
        c.execute("INSERT INTO tabela_gastos (data, categoria, valor, descricao) VALUES "
                     "(?, ?, ?, ?)", (data_obj, self.gastocategoria.text,
                                      valor_em_reais, self.gastodescricao.text))
        c.close()
        conn.commit()
        self.gastodata.text = ""
        self.gastocategoria.text = ""
        self.gastovalor.text = ""
        self.gastodescricao.text = ""

    def gastos_na_tela(self):
        conn = sqlite3.connect('gastos.db')
        c = conn.cursor()
        c.execute('SELECT * FROM tabela_gastos ORDER BY data DESC')
        dados_tabela = c.fetchall()

        self.ids.teladegastos.clear_widgets()

        for linha in dados_tabela:
            linha = list(linha)
            linha = str(linha)
            virgula = ","
            aspas = "'"
            colchete1 = "["
            colchete2 = "]"
            linha = str.replace(linha, virgula, " ")
            linha = str.replace(linha, aspas, " ")
            linha = str.replace(linha, colchete1, " ")
            linha = str.replace(linha, colchete2, " ")

            label = Label(text=(linha),text_size= self.size, halign= 'left',
            valign= 'center', size_hint= (1, 0.1), padding=(40,0))
            print(linha)
            self.ids.teladegastos.add_widget(label)

        c.close()
        conn.commit()




    def categoria_escolhida(gastocategoria, text):
        print("categoria selecionada")
        print(f" a categoria selecionada é {text}")
        return text

    def categoria(self):
        sm.current = "Categoria"


    def meses(self):
        sm.current = "Meses"

  # =================================== CATEGORIAS
class PaginaCategoria(Screen):
    layout = ObjectProperty()
    spinner = ObjectProperty()

    with open('cadastro.txt', 'r') as arquivo:
        linhas = arquivo.readlines()
    listadecategorias = [linha.strip() for linha in linhas]
    print(listadecategorias)

    def cadastrar_categoria(self):
        if self.cadastro.text == "":
            return
        print(f"a categoria é: {self.cadastro.text}")
        self.listadecategorias.append(self.cadastro.text)
        with open('cadastro.txt', 'a') as arquivo:
            arquivo.write(f"{self.cadastro.text}\n")
        print(f"a lista é: {self.listadecategorias}")
        self.ids.spinner.values = self.listadecategorias

    def atualizar_cadastro(self):
        self.ids.spinner.values = self.listadecategorias


    def principal(self):
        sm.current = "Principal"

    def limpar_tabela(self):
        conn = sqlite3.connect('gastos.db')
        c = conn.cursor()
        c.execute("DELETE FROM tabela_gastos")
        conn.commit()
        conn.close()

    def deletar_gasto(self):
        valor = "R$ 1000"
        conn = sqlite3.connect('gastos.db')
        c = conn.cursor()
        c.execute('DELETE FROM tabela_gastos WHERE valor = ?', (valor,))
        conn.commit()
        conn.close()

    def valor_meses(self, ctg):
        meses = ("Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro")
        meses_numero = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')
        conn = sqlite3.connect('gastos.db')
        c = conn.cursor()
        pos_y = 600
        print(ctg)
        self.ids.layout2.clear_widgets()
        for x, y in zip(meses, meses_numero):
            c.execute("SELECT valor FROM tabela_gastos WHERE strftime('%m', data) = ? AND categoria = ?", (y, ctg))
            gastos = c.fetchall()
            print(gastos)
            gastos = list(i[0] for i in gastos)
            print(x)
            soma_gastos = sum(gastos)
            print(soma_gastos)

            label = Label(text=f"{x} = {soma_gastos}", size_hint= (0.5, 0.1), pos=(100, pos_y))
            self.ids.layout2.add_widget(label)
            pos_y -= 50
        conn.close()


    def categoria_selecionada(spinner, text):
        print("categoria selecionada")
        print(f" a categoria selecionada é {text}")
        return text








class PaginaMeses(Screen):
    def principal(self):
        sm.current = "Principal"

    def categoria(self):
        sm.current = "Categoria"


class WindowManager(ScreenManager):
    pass


# ============== POP-UPS ============================

class NovaCategoria(Popup):
    pass

def novo_gasto():
    pass


# ============== GERENCIAMENTO DE PÁGINAS ===========

sm = WindowManager()

sm.add_widget(PaginaPrincipal(name="Principal"))
sm.add_widget(PaginaCategoria(name="Categoria"))
sm.add_widget(PaginaMeses(name="Meses"))

sm.current = 'Principal'
popup = NovaCategoria()




# db = DataBase()


class financasApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    financasApp().run()
