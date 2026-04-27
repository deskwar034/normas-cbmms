import io
import os
import re
import shutil
import zipfile
import tempfile
from pathlib import Path

import streamlit as st
from weasyprint import HTML


st.set_page_config(
    page_title="Converter HTML para PDF",
    page_icon="📄",
    layout="centered"
)

st.title("Converter HTML do ZIP para PDFs individualizados")
st.write(
    "Envie um arquivo `.zip` contendo arquivos `.htm` ou `.html`. "
    "O app converterá cada legislação para PDF e devolverá um ZIP com os PDFs renomeados."
)


MAPA_LEGISLACAO = {
    "05171488494754fb0425879200658446.htm": "DECRETO Nº 15.808 DE 18/11/2021",
    "0b478194a9fa934b04256e2d00666b9b.htm": "DECRETO Nº 1.093 DE 12/06/1981",
    "13310ab647c47daa04256e2d00689959.htm": "DECRETO Nº 5.620 DE 11/09/1990",
    "1df60fdb2f31d7aa04256e450002ea59.htm": "LEI Nº 61 DE 07/05/1980",
    "1ef390d986f31d7004257694003ac7c1.htm": "LEI Nº 3.808 DE 18/12/2009",
    "28c06bbcc434f3e60425796f0048793a.htm": "DECRETO Nº 13.329 DE 22/12/2011",
    "2ff62ce8864ba79404256e450002e92a.htm": "LEI Nº 105 DE 01/07/1980",
    "35480c7edb8b81b304256e2d0068978e.htm": "DECRETO Nº 5.622 DE 11/09/1990",
    "3c6fc5ac7be9dc990425811e0040313c.htm": "DECRETO Nº 14.734 DE 11/05/2017",
    "3d5ebc5c530eb32504256ed9004b6f27.htm": "DECRETO Nº 11.657 DE 21/07/2004",
    "3efddd0513a9c08904256dbf00529158.htm": "DECRETO Nº 11.439 DE 13/10/2003",
    "3f47e3a94b54d3270425881a00431c5f.htm": "DECRETO Nº 15.913 DE 31/03/2022",
    "4bd713ec1f24db3e84257b2400460490.htm": "DECRETO Nº 13.571 DE 28/02/2013",
    "51b719740d09e90f04256bff005e94b0.htm": "DECRETO Nº 10.159 DE 12/12/2000",
    "56d087c4ea88f54904256bfb007a29d6.htm": "DECRETO Nº 10.529 DE 29/10/2001",
    "61a3a68f0a65cd2c04256e2d006897d6.htm": "DECRETO Nº 5.523 DE 12/06/1990",
    "6aa97dec0dfb8fd304256bfd005b7dc6.htm": "DECRETO Nº 10.769 DE 09/05/2002",
    "6bdccb74e40d391004256e2d00666afd.htm": "DECRETO Nº 1.261 DE 02/10/1981",
    "6ef4beea872cb37104256e2d00666bb9.htm": "DECRETO Nº 1.260 DE 02/10/1981",
    "72db1a79472182b10425744b00502c34.htm": "LEI COMPLEMENTAR Nº 127 DE 15/05/2008",
    "75d11e4bbfc1a0d704256e2d006899b9.htm": "DECRETO Nº 5.548 DE 04/07/1990",
    "82aeaec8cbf0f58304257f11004c4ecc.htm": "DECRETO Nº 14.332 DE 03/12/2015",
    "837bdd99ce6fac9784257b6e0043a514.htm": "DECRETO Nº 13.631 DE 16/05/2013",
    "876029431575da5d04256e2d0066f2dc.htm": "DECRETO Nº 2.426 DE 23/01/1983",
    "9ddc78a75720592804256e2d006899e6.htm": "DECRETO Nº 5.698 DE 21/11/1990",
    "a3716fd888a4f98f04257d9e00425cbb.htm": "DECRETO Nº 14.089 DE 27/11/2014",
    "a632c6aa46d10dc704256e2d00691e4d.htm": "DECRETO Nº 6.369 DE 21/02/1992",
    "acfc79dc10698f0104256e450002ea9a.htm": "LEI Nº 1.366 DE 11/05/1993",
    "b3678c37ed4078e5042574f00061bb33.htm": "DECRETO Nº 12.638 DE 24/10/2008",
    "b5e0202419d9367904258645007921ca.htm": "LEI COMPLEMENTAR Nº 279 DE 17/12/2020",
    "bc50f1d02c3db61204256bfb001040d2.htm": "DECRETO Nº 10.768 DE 09/05/2002",
    "bc7f1c541f838cd104257cb70063d739.htm": "LEI COMPLEMENTAR Nº 188 DE 03/04/2014",
    "c3a24e74f4f057f504256e2d006987a1.htm": "DECRETO Nº 7.963 DE 30/09/1994",
    "d10418.htm": "DECRETO Nº 10.418, DE 7 DE JULHO DE 2020",
    "d4346.htm": "DECRETO Nº 4.346, DE 26 DE AGOSTO DE 2002",
    "d5590886b0385f4804256e820042b2c8.htm": "DECRETO Nº 11.591 DE 23/04/2004",
    "d9847.htm": "DECRETO Nº 9.847, DE 25 DE JUNHO DE 2019",
    "dc393e7feb95345204256e2d00691b3f.htm": "DECRETO Nº 6.250 DE 09/12/1991",
    "dd37adf9cdcd65190425843c004353bd.htm": "DECRETO Nº 15.262 DE 18/07/2019",
    "de547de4ca866323042586bc0042040d.htm": "DECRETO Nº 15.654 DE 15/04/2021",
    "Decreto-n#U00ba-1.775-de-2-de-julho-de-1856.pdf": "DECRETO Nº 1.775, DE 2 DE JULHO DE 1856",
    "del0667.htm": "DECRETO-LEI Nº 667, DE 2 DE JULHO DE 1969",
    "del1001.htm": "DECRETO-LEI Nº 1.001, DE 21 DE OUTUBRO DE 1969 — Código Penal Militar",
    "del1002.htm": "DECRETO-LEI Nº 1.002, DE 21 DE OUTUBRO DE 1969 — Código de Processo Penal Militar",
    "dfde24a4767ddcbf04257e4b006c0233.htm": "CONSTITUIÇÃO ESTADUAL DE MATO GROSSO DO SUL, DE 5 DE OUTUBRO DE 1989",
    "ecec9e418b34b2f404258036003f1678.htm": "DECRETO Nº 14.568 DE 21/09/2016",
    "edc7e25ce721820704256e2d0068984e.htm": "DECRETO Nº 5.680 DE 25/10/1990",
    "f32fb9368ed3f67a84257b4a0044bfd3.htm": "LEI Nº 4.335 DE 10/04/2013",
    "f9e1bfd075759c3f04257229004cc952.htm": "DECRETO Nº 12.185 DE 16/11/2006",
    "fafddb48ebfab17704256ed9004ffc18.htm": "DECRETO Nº 11.656 DE 21/07/2004",
    "fd4157c561ee128504256e2d0068990e.htm": "DECRETO Nº 5.621 DE 11/09/1990",
    "fd76dead368931d8042580890043babc.htm": "LEI Nº 4.947 DE 13/12/2016",
    "ff6e653dca4d5a630425729e006f48e7.htm": "LEI COMPLEMENTAR Nº 053 DE 30/08/1990",
    "l10029.htm": "LEI Nº 10.029, DE 20 DE OUTUBRO DE 2000",
    "l13425.htm": "LEI Nº 13.425, DE 30 DE MARÇO DE 2017",
    "l13675.htm": "LEI Nº 13.675, DE 11 DE JUNHO DE 2018",
    "l13954.htm": "LEI Nº 13.954, DE 16 DE DEZEMBRO DE 2019",
    "l13967.htm": "LEI Nº 13.967, DE 26 DE DEZEMBRO DE 2019",
    "l8429.htm": "LEI Nº 8.429, DE 2 DE JUNHO DE 1992",
    "l8666cons.htm": "LEI Nº 8.666, DE 21 DE JUNHO DE 1993",
    "regulamento-de-uniformes.html": "Regulamento de Uniformes — DECRETO Nº 14.091, DE 28 DE NOVEMBRO DE 2014",
}


def nome_pdf_seguro(nome: str) -> str:
    """
    Transforma o nome da legislação em nome de arquivo válido.
    Exemplo:
    DECRETO Nº 15.808 DE 18/11/2021
    vira:
    DECRETO Nº 15.808 DE 18-11-2021.pdf
    """
    nome = nome.strip()

    substituicoes = {
        "/": "-",
        "\\": "-",
        ":": " -",
        "*": "",
        "?": "",
        '"': "",
        "<": "",
        ">": "",
        "|": "-",
        "\n": " ",
        "\r": " ",
        "\t": " ",
    }

    for antigo, novo in substituicoes.items():
        nome = nome.replace(antigo, novo)

    nome = re.sub(r"\s+", " ", nome).strip()
    nome = nome.rstrip(".")

    if len(nome) > 180:
        nome = nome[:180].strip()

    return f"{nome}.pdf"


def evitar_nome_repetido(nome: str, usados: set[str]) -> str:
    """
    Evita sobrescrever PDFs caso dois arquivos gerem o mesmo nome final.
    """
    if nome not in usados:
        usados.add(nome)
        return nome

    base = nome[:-4]
    contador = 2

    while True:
        novo_nome = f"{base} ({contador}).pdf"
        if novo_nome not in usados:
            usados.add(novo_nome)
            return novo_nome
        contador += 1


def extrair_zip_com_seguranca(zip_path: Path, destino: Path) -> None:
    """
    Extrai o ZIP evitando caminhos perigosos como ../../arquivo.
    """
    with zipfile.ZipFile(zip_path, "r") as z:
        for item in z.infolist():
            caminho_destino = destino / item.filename
            caminho_destino_resolvido = caminho_destino.resolve()

            if not str(caminho_destino_resolvido).startswith(str(destino.resolve())):
                raise RuntimeError(f"Arquivo inseguro no ZIP: {item.filename}")

            z.extract(item, destino)


def encontrar_arquivos_processaveis(pasta: Path) -> list[Path]:
    extensoes = {".html", ".htm", ".xhtml", ".pdf"}
    arquivos = []

    for caminho in pasta.rglob("*"):
        if caminho.is_file() and caminho.suffix.lower() in extensoes:
            if "__MACOSX" not in caminho.parts:
                arquivos.append(caminho)

    return sorted(arquivos, key=lambda p: p.name.lower())


def converter_html_para_pdf(arquivo_html: Path, arquivo_pdf: Path) -> None:
    """
    Converte HTML para PDF.
    O base_url permite que imagens/CSS relativos dentro do ZIP sejam encontrados.
    """
    HTML(filename=str(arquivo_html), base_url=str(arquivo_html.parent)).write_pdf(str(arquivo_pdf))


def processar_zip(uploaded_file) -> tuple[bytes, list[str], list[str], list[str]]:
    """
    Retorna:
    - bytes do ZIP final
    - lista de PDFs gerados
    - lista de arquivos ignorados por não estarem na tabela
    - lista de erros
    """
    pdfs_gerados = []
    ignorados = []
    erros = []
    nomes_usados = set()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        zip_entrada = tmp_dir / "entrada.zip"
        pasta_extraida = tmp_dir / "extraido"
        pasta_saida = tmp_dir / "saida"

        pasta_extraida.mkdir()
        pasta_saida.mkdir()

        zip_entrada.write_bytes(uploaded_file.getvalue())

        extrair_zip_com_seguranca(zip_entrada, pasta_extraida)

        arquivos = encontrar_arquivos_processaveis(pasta_extraida)

        for arquivo in arquivos:
            nome_original = arquivo.name
            nome_original_lower = nome_original.lower()

            mapa_normalizado = {
                chave.lower(): valor
                for chave, valor in MAPA_LEGISLACAO.items()
            }

            if nome_original_lower not in mapa_normalizado:
                ignorados.append(nome_original)
                continue

            legislacao = mapa_normalizado[nome_original_lower]
            nome_pdf = nome_pdf_seguro(legislacao)
            nome_pdf = evitar_nome_repetido(nome_pdf, nomes_usados)

            destino_pdf = pasta_saida / nome_pdf

            try:
                if arquivo.suffix.lower() == ".pdf":
                    shutil.copy2(arquivo, destino_pdf)
                else:
                    converter_html_para_pdf(arquivo, destino_pdf)

                pdfs_gerados.append(nome_pdf)

            except Exception as e:
                erros.append(f"{nome_original}: {e}")

        buffer_zip = io.BytesIO()

        with zipfile.ZipFile(buffer_zip, "w", compression=zipfile.ZIP_DEFLATED) as zip_saida:
            for pdf in sorted(pasta_saida.glob("*.pdf")):
                zip_saida.write(pdf, arcname=pdf.name)

        buffer_zip.seek(0)
        return buffer_zip.getvalue(), pdfs_gerados, ignorados, erros


arquivo_zip = st.file_uploader(
    "Envie o ZIP com os arquivos HTML",
    type=["zip"]
)

if arquivo_zip is not None:
    if st.button("Converter para PDF"):
        with st.spinner("Convertendo arquivos..."):
            try:
                zip_final, pdfs_gerados, ignorados, erros = processar_zip(arquivo_zip)

                if pdfs_gerados:
                    st.success(f"{len(pdfs_gerados)} PDFs foram gerados com sucesso.")

                    st.download_button(
                        label="Baixar ZIP com PDFs",
                        data=zip_final,
                        file_name="legislacoes_em_pdf.zip",
                        mime="application/zip"
                    )

                    with st.expander("Ver PDFs gerados"):
                        for nome in pdfs_gerados:
                            st.write(f"✅ {nome}")
                else:
                    st.warning("Nenhum PDF foi gerado.")

                if ignorados:
                    with st.expander(f"Arquivos ignorados por não estarem na tabela ({len(ignorados)})"):
                        for nome in ignorados:
                            st.write(f"⚠️ {nome}")

                if erros:
                    with st.expander(f"Erros durante a conversão ({len(erros)})"):
                        for erro in erros:
                            st.write(f"❌ {erro}")

            except zipfile.BadZipFile:
                st.error("O arquivo enviado não é um ZIP válido.")
            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")
