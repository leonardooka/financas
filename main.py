import locale
import textwrap

from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

Config.set('graphics', 'width', '540')
Config.set('graphics', 'height', '800')


from kivy.core.window import Window
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

# ===================== CLASSES E PÁGINAS ==========================================


conn = sqlite3.connect('gastos.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS tabela_gastos (data DATE, categoria, 
    descricao, valor REAL)''')
c.close()
conn.commit()


# ==================================================== PRINCIPAL
class PaginaPrincipal(Screen, FloatLayout):

    def categoria(self):
        sm.current = "Categoria"

    def meses(self):
        sm.current = "Meses"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self.on_tab_pressionado)

    def on_tab_pressionado(self, teclado, codigo, *args):
        if codigo in (9, 13):
            if self.gastodata.focus:
                self.gastovalor.focus = True
                self.gastovalor.cursor = (0, 0)
            elif self.gastovalor.focus:
                self.gastodescricao.focus = True
                self.gastodescricao.cursor = (0, 0)
    with open('cadastro.txt', 'r') as arquivo:
        linhas = arquivo.readlines()
    categorias = [linha.strip() for linha in linhas]
    print(categorias)

# ----------------------------------------------
    def incluir_gasto(self):
        if self.gastodata.text == "":
            return
        data_string = self.gastodata.text.replace('/', '-')
        data_obj = datetime.strptime(data_string, '%d-%m-%Y')
        # locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        # valor_em_reais = locale.currency(float(self.gastovalor.text), grouping=True)
        conn = sqlite3.connect('gastos.db')
        c = conn.cursor()
        c.execute("INSERT INTO tabela_gastos (data, categoria, valor, descricao) VALUES "
                  "(?, ?, ?, ?)", (data_obj, self.gastocategoria.text,
                                   self.gastovalor.text, self.gastodescricao.text))
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
        self.ids.teladegastos.bind(minimum_height=self.ids.teladegastos.setter('height'))
        self.ids.teladegastos.clear_widgets()

        for linha in dados_tabela:
            linha = list(linha)
            data = str(linha[0])
            data = str.replace(data, "00:00:00", " ")
            categoria = linha[1]
            descricao = linha[2]
            valor = float(linha[3])
            linha = str(linha)
            print(f"str de {linha}")

            gasto_texto = f"{data}   {categoria:<15}{descricao:<20}R$ {valor:.2f}"  # método espaçamento

            label = Label(text=(gasto_texto), font_name='ttf/DejaVuSansMono-Oblique.ttf',
                          font_size=17, text_size=self.size, halign='left',
                          valign='center', size_hint=(1, 0.3), padding=(40, 0))
            print(gasto_texto)
            self.ids.teladegastos.add_widget(label)

        c.close()
        conn.commit()

    def categoria_escolhida(gastocategoria, text):
        print("categoria selecionada")
        print(f" a categoria selecionada é {text}")
        return text

# ======================================================= CATEGORIAS
class PaginaCategoria(Screen):

    def principal(self):
        sm.current = "Principal"

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

    def valor_meses(self, ctg):
        meses = (
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro",
        "Dezembro")
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
            soma_gastos = f"RS {sum(gastos):.2f}"
            print(soma_gastos)

            label = Label(text=f"{x:<15} = {soma_gastos}", font_name='fonts/mono/RedHatMono-Regular.ttf',
                          text_size=self.size, halign='left', valign='center', size_hint=(0.5, 0.1),
                          pos=(self.width / 3, pos_y))
            self.ids.layout2.add_widget(label)
            pos_y -= 50
        conn.close()

    def categoria_selecionada(spinner, text):
        print("categoria selecionada")
        print(f" a categoria selecionada é {text}")
        return text

    def popup_excluir(self, instance):
        layout_botoes = BoxLayout(orientation='horizontal')

        # Adição de botões ao layout
        botao1 = Button(text='Não', on_press=lambda x: self.fechar_popup(x, layout_botoes))
        botao2 = Button(text='Sim', on_press=self.excluir_categoria(), on_release=lambda x: self.fechar_popup(x, layout_botoes))


        layout_botoes.add_widget(botao1)
        layout_botoes.add_widget(botao2)

        popup = Popup(title=f'Tem certeza em excluir {self.spinner.text}?',
                    content=layout_botoes,
                     size=(400, 400))
        self.popup = popup
        self.popup.open()

    def fechar_popup(self, instance, layout_botoes):
        self.popup.dismiss()

    def excluir_categoria(self):
        ctg = []
        linhas = []
        categoria = self.spinner.text
        with open('cadastro.txt', 'r') as arquivo:
            linhas = arquivo.readlines()
        for linha in linhas:
            linha = str.replace(linha, '\n', '')
            if linha != categoria:
                ctg.append(f"{linha}\n")

        with open('cadastro.txt', 'w') as arquivo2:
            arquivo2.writelines(ctg)

        with open('cadastro.txt', 'r') as arquivo3:
            linhas2 = arquivo3.readlines()
        self.listadecategorias = [linha2.strip() for linha2 in linhas2]
        print(self.listadecategorias)

    # ------------------- PARA ADMINISTRAR A DATABASE -----------
    def limpar_tabela(self):
        conn = sqlite3.connect('gastos.db')
        c = conn.cursor()
        c.execute("DELETE FROM tabela_gastos")
        conn.commit()
        conn.close()

    def deletar_gasto(self):
        valor = ""
        conn = sqlite3.connect('gastos.db')
        c = conn.cursor()
        c.execute('DELETE FROM tabela_gastos WHERE valor = ?', (valor,))
        conn.commit()
        conn.close()


# ============================================================= MESES
class PaginaMeses(Screen):
    def principal(self):
        sm.current = "Principal"

    def categoria(self):
        sm.current = "Categoria"



    # -------------------------------------------

    mes = ObjectProperty()
    scrollmes = ObjectProperty()
    historico = ObjectProperty()
    ctgsoma = ObjectProperty()

    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro",
             "Novembro", "Dezembro"]
    mes_relacionado = {"Janeiro": '01', "Fevereiro": '02', "Março": '03', "Abril": '04', "Maio": '05',
                       "Junho": '06', "Julho": '07', "Agosto": '08', "Setembro": '09', "Outubro": '10',
                       "Novembro": '11', "Dezembro": '12'}

    paginacategoria = PaginaCategoria()
    listadecategorias_clone = paginacategoria.listadecategorias

    # -------------------------------------------

    def atualizar_cadastro(self):
        self.ids.mes.values = self.meses

    def historico_do_mes(self):
        mes_procurado = self.mes_relacionado.get(self.mes.text)
        conn = sqlite3.connect('gastos.db')
        c = conn.cursor()
        c.execute("SELECT * FROM tabela_gastos WHERE strftime('%m', data) = ? ORDER BY data DESC", (mes_procurado,))
        dados_tabela = c.fetchall()
        self.ids.historico.bind(minimum_height=self.ids.historico.setter('height'))
        self.ids.historico.clear_widgets()

        for linha in dados_tabela:
            linha = list(linha)
            data = str(linha[0])
            data = str.replace(data, "00:00:00", " ")
            categoria = linha[1]
            descricao = linha[2]
            valor = float(linha[3])
            linha = str(linha)
            print(f"str de {linha}")

            gasto_texto = f"{data}  {categoria:<15}{descricao:<20}R$ {valor:.2f}"  # método espaçamento

            label = Label(text=(gasto_texto), font_name='ttf/DejaVuSansMono-Oblique.ttf',
                          font_size=17, text_size=self.size, halign='left',
                          valign='center', size_hint=(1, 0.3), padding=(40, 0))
            print(gasto_texto)
            self.ids.historico.add_widget(label)
        conn.commit()
        conn.close()

    def mes_selecionado(spinner, text):
        print("mês selecionado")
        print(f" o mês selecionado é {text}")
        return text

    def total_categorias(self):
        mes_procurado = self.mes_relacionado.get(self.mes.text)
        pos_y = 300

        conn = sqlite3.connect('gastos.db')

        self.ids.ctgsoma.clear_widgets()
        c = conn.cursor()
        for ctg in self.listadecategorias_clone:
            c.execute("SELECT valor FROM tabela_gastos WHERE strftime('%m', data) = ? AND categoria = ?", (mes_procurado, ctg))
            gastos = c.fetchall()
            print(gastos)
            gastos = list(i[0] for i in gastos)
            soma_gastos = f"RS {sum(gastos):.2f}"
            print(f"{ctg} = {soma_gastos}")
            label = Label(text=f"{ctg:<15} = {soma_gastos}", font_name='fonts/mono/RedHatMono-Regular.ttf',
                          text_size=self.ctgsoma.size, padding= 40, halign='left', valign='center', size_hint=(1, 0.1),
                          pos=(300 , pos_y))
            self.ids.ctgsoma.add_widget(label)
            pos_y -= 50
        conn.commit()
        conn.close()


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
