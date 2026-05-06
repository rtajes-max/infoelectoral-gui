"""Diálogo «Acerca de» con créditos prominentes a Jaime Obregón."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)

from .. import __build_time__, __version__


ABOUT_HTML = """
<h2>infoelectoral · visor de microdatos del Ministerio</h2>
<p><b>Versión:</b> {version} <span style="color:#888;">(build {build})</span></p>

<h3>🙏 Agradecimientos</h3>
<p>
Esta aplicación se construye sobre el extraordinario trabajo de
<b><a href="https://github.com/JaimeObregon/infoelectoral">Jaime Gómez-Obregón</a></b>
y su proyecto <a href="https://github.com/JaimeObregon/infoelectoral">infoelectoral</a>.
Sin su esfuerzo de ingeniería inversa de los ficheros <code>.DAT</code> del Ministerio
del Interior, su trabajo de catalogación y los ficheros que ha publicado al dominio
público, esta aplicación <b>simplemente no existiría</b>.
</p>

<p>
El parser que viaja dentro de este programa es una traducción fiel a Python del código
PHP de Jaime, incluyendo todos los <i>fixups</i> que él descubrió en años de trabajo
con los datos. La spec de campos, las tablas de municipios INE, los códigos históricos,
las decodificaciones de candidaturas, todo viene de su trabajo previo.
</p>

<p style="text-align:center; font-size:14px; color:#1a3d7c;">
<b>Gracias, Jaime, por hacer accesibles los datos electorales españoles.</b>
</p>

<h3>📜 Licencia</h3>
<p>
GNU AGPL-3.0 (la misma licencia que el proyecto original de Jaime).
Esta es una obra <i>derivada</i> y se redistribuye bajo los mismos términos.
</p>

<h3>🔗 Enlaces</h3>
<ul>
  <li>Proyecto original (Jaime Obregón): <a href="https://github.com/JaimeObregon/infoelectoral">github.com/JaimeObregon/infoelectoral</a></li>
  <li>Este proyecto:
      <a href="https://github.com/JaimeObregon/infoelectoral">[ver README]</a></li>
  <li>Datos del Ministerio del Interior:
      <a href="https://www.infoelectoral.mir.es/infoelectoral/min/">infoelectoral.mir.es</a></li>
</ul>

<h3>👥 Créditos</h3>
<ul>
  <li><b>Especificación de formatos y parser de referencia</b>: Jaime Gómez-Obregón
      (<a href="https://twitter.com/JaimeObregon">@JaimeObregon</a>).</li>
  <li><b>Tablas de municipios INE</b>: Instituto Nacional de Estadística, recopiladas
      y mantenidas por Jaime.</li>
  <li><b>Datos originales</b>: Ministerio del Interior de España (<i>infoelectoral</i>).</li>
  <li><b>GUI y empaquetado</b>: contribuidores de este proyecto.</li>
</ul>
"""


class AboutDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Acerca de infoelectoral")
        self.resize(620, 600)

        layout = QVBoxLayout(self)
        label = QLabel(ABOUT_HTML.format(version=__version__, build=__build_time__))
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        label.setOpenExternalLinks(True)
        layout.addWidget(label, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        # En este diálogo solo hay Close
        if buttons.button(QDialogButtonBox.Close):
            buttons.button(QDialogButtonBox.Close).clicked.connect(self.accept)
        layout.addWidget(buttons)
