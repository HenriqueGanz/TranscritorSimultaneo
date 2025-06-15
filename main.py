from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRectangleFlatIconButton, MDIconButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from datetime import datetime
from transcricao import transcrever_audio

Window.size = (360, 640)

class TranscricaoApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.transcritor = None
        self.texto_acumulado = ""
        self.dark_mode = False

        self.root_layout = MDBoxLayout(orientation="vertical", padding=10, spacing=10)

        # Topo com botão de tema
        topo_layout = MDBoxLayout(orientation="horizontal", size_hint=(1, 0.08), padding=(0, 0, 10, 0))
        self.btn_tema = MDIconButton(
            icon="moon-waning-crescent",
            pos_hint={"center_y": 0.5},
            on_release=self.toggle_tema
        )
        topo_layout.add_widget(MDLabel(text="Transcrição", halign="left", theme_text_color="Primary"))
        topo_layout.add_widget(self.btn_tema)

        # Scroll com label
        self.scroll = MDScrollView(size_hint=(1, 0.67))
        self.label = MDLabel(
            text="Clique no microfone para começar a transcrição.",
            size_hint_y=None,
            halign="left",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            font_style="Body1"
        )
        self.label.bind(texture_size=self.label.setter("size"))
        self.scroll.add_widget(self.label)

        # Botão de transcrição
        self.btn_transcricao = MDRectangleFlatIconButton(
            text="Iniciar",
            icon="microphone",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.6, 1, 1),
            text_color=(1, 1, 1, 1),
            icon_color=(1, 1, 1, 1),
            size_hint=(1, 0.12),
            on_release=self.toggle_transcricao
        )

        # Botões de limpar/salvar
        botoes_layout = MDGridLayout(cols=2, size_hint=(1, 0.12), spacing=dp(10))

        self.btn_limpar = MDRectangleFlatIconButton(
            text="Limpar",
            icon="delete",
            md_bg_color=(1, 0.4, 0.4, 1),
            text_color=(1, 1, 1, 1),
            icon_color=(1, 1, 1, 1),
            on_release=self.limpar_texto
        )
        self.btn_salvar = MDRectangleFlatIconButton(
            text="Salvar",
            icon="content-save",
            md_bg_color=(0.3, 0.8, 0.4, 1),
            text_color=(1, 1, 1, 1),
            icon_color=(1, 1, 1, 1),
            on_release=self.salvar_texto
        )

        botoes_layout.add_widget(self.btn_limpar)
        botoes_layout.add_widget(self.btn_salvar)

        self.root_layout.add_widget(topo_layout)
        self.root_layout.add_widget(self.scroll)
        self.root_layout.add_widget(self.btn_transcricao)
        self.root_layout.add_widget(botoes_layout)

        return self.root_layout

    def toggle_tema(self, instance):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.theme_cls.theme_style = "Dark"
            self.label.text_color = (1, 1, 1, 1)
            self.btn_tema.icon = "white-balance-sunny"  # Sol
        else:
            self.theme_cls.theme_style = "Light"
            self.label.text_color = (0, 0, 0, 1)
            self.btn_tema.icon = "moon-waning-crescent"  # Lua

    def toggle_transcricao(self, instance):
        if self.transcritor is None:
            self.texto_acumulado = ""
            self.label.text = "🎤 Escutando..."
            self.btn_transcricao.text = "Parar"
            self.btn_transcricao.icon = "stop"
            self.btn_transcricao.md_bg_color = (0.1, 0.8, 0.1, 1)
            self.transcritor = transcrever_audio(self.receber_texto)
            self.transcritor.iniciar()
        else:
            self.transcritor.parar()
            self.transcritor = None
            self.btn_transcricao.text = "Iniciar"
            self.btn_transcricao.icon = "microphone"
            self.btn_transcricao.md_bg_color = (0.2, 0.6, 1, 1)

    def receber_texto(self, texto):
        if texto.startswith("[Pausado por inatividade"):
            Clock.schedule_once(lambda dt: self.interromper_transcricao())
        Clock.schedule_once(lambda dt: self.atualizar_interface(texto))

    def atualizar_interface(self, novo_texto):
        self.texto_acumulado += f"{novo_texto}\n"
        self.label.text = self.texto_acumulado

    def limpar_texto(self, _):
        self.texto_acumulado = ""
        self.label.text = ""
        self.mostrar_dialogo("Transcrição limpa.")

    def salvar_texto(self, _):
        agora = datetime.now().strftime('%Y%m%d_%H%M%S')
        with open(f"transcricao_{agora}.txt", "w", encoding="utf-8") as f:
            f.write(self.texto_acumulado)
        self.mostrar_dialogo("Transcrição salva com sucesso!")

    def interromper_transcricao(self):
        if self.transcritor:
            self.transcritor.parar()
            self.transcritor = None
        self.btn_transcricao.text = "Iniciar"
        self.btn_transcricao.icon = "microphone"
        self.btn_transcricao.md_bg_color = (0.2, 0.6, 1, 1)
        self.mostrar_dialogo("Transcrição pausada por inatividade.")

    def mostrar_dialogo(self, mensagem, titulo="Aviso"):
        dialog = MDDialog(
            title=titulo,
            text=mensagem,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()

if __name__ == '__main__':
    TranscricaoApp().run()
