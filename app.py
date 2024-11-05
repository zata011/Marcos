import flet as ft
from fpdf import FPDF
import os
import pandas as pd

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Tabla de Datos', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def main(page: ft.Page):
    page.bgcolor = "#ffffff"
    lista_de_compras = []
    page.scroll = ft.ScrollMode.ALWAYS

    logo_path = os.path.join(os.path.dirname(__file__), "img/carrito.png")
    logo = ft.Image(src=logo_path, width=200, height=150)

    page.window.width = 600
    page.window.height = 400
    page.window.resizable = False
    page.title = "Lista de Compras Super Ypacarai"

    selector_archivos = ft.FilePicker(on_result=lambda e: guardar_archivo(e))
    page.overlay.append(selector_archivos)

    def mostrar_dialogo_error():
        def cerrar_dialogo(e):
            page.dialog.open = False
            page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Error", color="#000000"),
            content=ft.Text("No puedes agregar un ítem en blanco.", color="#000000"),
            actions=[ft.TextButton("OK", on_click=cerrar_dialogo, style=ft.ButtonStyle(bgcolor="000000"))],
            open=True
        )
        page.update()

    def agregar_clic(e):
        if not nueva_tarea.value.strip():
            mostrar_dialogo_error()
            return

        item = crear_item(nueva_tarea.value)
        lista_de_compras.append(nueva_tarea.value)
        vista_lista.controls.append(item)
        nueva_tarea.value = ""
        nueva_tarea.focus()
        page.update()
        actualizar_botones()

    def crear_item(texto):
        checkbox = ft.Checkbox(label=texto, fill_color="#000000")
        boton_editar = ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e: editar_clic(e, checkbox, item), icon_color="#000000")
        boton_eliminar = ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e: eliminar_clic(e, item, texto), icon_color="#000000")
        item = ft.Row([checkbox, boton_editar, boton_eliminar], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        return item

    def editar_clic(e, checkbox, item):
        nuevo_valor = ft.TextField(value=checkbox.label, width=300, bgcolor="#ffffff")
        boton_guardar = ft.IconButton(icon=ft.icons.SAVE, on_click=lambda e: guardar_clic(e, checkbox, nuevo_valor, item), icon_color="#000000")
        boton_cancelar = ft.IconButton(icon=ft.icons.CANCEL, on_click=lambda e: cancelar_clic(e, checkbox, item), icon_color="#000000")
        item.controls = [nuevo_valor, boton_guardar, boton_cancelar]
        page.update()

    def guardar_clic(e, checkbox, nuevo_valor, item):
        checkbox.label = nuevo_valor.value
        item.controls = [
            checkbox,
            ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e: editar_clic(e, checkbox, item), icon_color="#000000"),
            ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e: eliminar_clic(e, item, checkbox.label), icon_color="#000000")
        ]
        page.update()

    def cancelar_clic(e, checkbox, item):
        item.controls = [
            checkbox,
            ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e: editar_clic(e, checkbox, item), icon_color="#000000"),
            ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e: eliminar_clic(e, item, checkbox.label), icon_color="#000000")
        ]
        page.update()

    def eliminar_clic(e, item, texto):
        lista_de_compras.remove(texto)
        vista_lista.controls.remove(item)
        page.update()
        actualizar_botones()

    def guardar_pdf(e):
        if e.path:
            pdf = PDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for item in lista_de_compras:
                pdf.cell(0, 10, item, ln=True)
            pdf.output(e.path)

            page.snack_bar = ft.SnackBar(
                content=ft.Text("Lista guardada como PDF"),
                bgcolor="#000000"
            )
            page.snack_bar.open = True
            page.update()

    def guardar_excel(e):
        if e.path:
            df = pd.DataFrame(lista_de_compras, columns=["Producto"])
            df.to_excel(e.path, index=False)

            page.snack_bar = ft.SnackBar(
                content=ft.Text("Lista guardada como Excel"),
                bgcolor="#000000"
            )
            page.snack_bar.open = True
            page.update()

    def guardar_archivo(e):
        if e.path:
            _, extension = os.path.splitext(e.path)
            if extension == ".pdf":
                guardar_pdf(e)
            elif extension == ".xlsx":
                guardar_excel(e)
            else:
                with open(e.path, "w") as file:
                    if extension == ".txt":
                        for item in lista_de_compras:
                            file.write(f"{item}\n")
                    elif extension == ".csv":
                        file.write("Ítem\n")
                        for item in lista_de_compras:
                            file.write(f"{item}\n")
                    elif extension == ".json":
                        import json
                        json.dump({"lista_de_compras": lista_de_compras}, file, indent=4)

                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Lista guardada como {extension}"),
                    bgcolor="#000000"
                )
                page.snack_bar.open = True
                page.update()

    def limpiar_lista(e):
        lista_de_compras.clear()
        vista_lista.controls.clear()
        page.update()
        actualizar_botones()

    def actualizar_botones():
        fila_botones.controls = [
            nueva_tarea,
            ft.ElevatedButton("Agregar", on_click=agregar_clic, bgcolor="#000000", color="white"),
            ft.ElevatedButton("Guardar como PDF", on_click=lambda e: selector_archivos.save_file(allowed_extensions=["pdf"]), bgcolor="#000000", color="white"),
            ft.ElevatedButton("Guardar como Excel", on_click=lambda e: selector_archivos.save_file(allowed_extensions=["xlsx"]), bgcolor="#000000", color="white")
        ]
        if lista_de_compras:
            boton_limpiar.visible = True
        else:
            boton_limpiar.visible = False
        page.update()

    nueva_tarea = ft.TextField(hint_text="Agregar Producto", width=250, bgcolor="#ffffff")

    boton_limpiar = ft.ElevatedButton(
        "Limpiar lista", on_click=limpiar_lista, bgcolor="#000000", 
        color="white", width=200, height=50, visible=False
    )

    texto_encabezado = ft.Text("Bienvenidos Super Ypacarai", size=20, weight=ft.FontWeight.BOLD, color="#000000")

    encabezado = ft.Column(
        [logo, texto_encabezado], 
        alignment=ft.MainAxisAlignment.CENTER, 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    fila_botones = ft.Row(
        [nueva_tarea, ft.ElevatedButton("Agregar", on_click=agregar_clic, bgcolor="#000000", color="white")],
        alignment=ft.MainAxisAlignment.CENTER
    )

    vista_lista = ft.Column([], expand=True, alignment=ft.MainAxisAlignment.START)

    contenedor = ft.Column(
        [encabezado, ft.Divider(height=20, color="ffffff"), fila_botones, boton_limpiar, vista_lista],
        expand=True, alignment=ft.MainAxisAlignment.CENTER, 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.add(contenedor)

ft.app(target=main)