import random
import time
from os import system

class Persona:
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad

    def modificar(self, nuevo_nombre, nueva_edad):
        self.nombre = nuevo_nombre
        self.edad = nueva_edad


class Tarea:
    def __init__(self, nombre, nivel, hora):
        self.nombre = nombre
        self.nivel = nivel
        self.hora = hora


personas = []  # lista de personas

tareas = []  # lista de tareas

asignaciones_guardadas = []  # lista de asignaciones


def login():
    intentos = 0
    usuario = "admin"
    password = "1234"

    print("Antes de continuar porfavor inicie sesion.")

    while intentos < 3:
        try:
            ingreseusuario = input("ingrese usuario: ")
        except (ValueError, KeyboardInterrupt):
            print("Ingrese caracter valido")
            continue

        try:
            ingresecontra = input("ingrese contraseña: ")
        except (ValueError, KeyboardInterrupt):
            print("Ingrese caracter valido")
            continue

        if ingresecontra == password and ingreseusuario == usuario:
            print("Acceso Exitoso")
            time.sleep(1)
            system('cls')
            menu()
            break
        else:
            print("Datos incorrectos")
            intentos += 1

        if intentos == 3:
            print("Cuenta bloqueada")
            break

    return


def menu():
    while True:
        print("Bienvenido")
        print("----------------------")
        print("Menu Principal")
        print("1.- Gestión de personas")
        print("2.- Gestión de tareas")
        print("3.- Asignaciones")
        print("4.- Salir")
        print("-------------------------------")
        try:
            opcion = int(input("Por favor seleccione una opcion: "))
        except (ValueError, KeyboardInterrupt):
            print("-----------------------")
            print("Ingrese caracter valido")
            print("-----------------------")
            continue

        if opcion == 1:
            gestionpersonas()  # se inicia la funcion de gestion de personas
        if opcion == 2:
            gestiontareas()  # se inicia la funcion de gestion de tareas
        if opcion == 3:
            asignaciones()  # se inicia la funcion de asignaciones
        if opcion == 4:
            break  # se rompe bucle y termina el programa

        #menu principal, se reiniciara hasta escoger una opcion




def gestionpersonas():  # funcion de gestion de personas

    while True:  # se reiniciara hasta escoger una opcion valida

        print("-------------------------------")
        print("Entraste a gestion de personas")
        print("-------------------------------")
        print("1.- Agregar persona")
        print("2.- Listar personas")
        print("3.- Modificar persona")
        print("4.- Quitar persona")
        print("5.- Volver al menu principal")
        print("-------------------------------")
        try:
            opcion = int(input("Por favor seleccione una opcion: "))
        except (ValueError, KeyboardInterrupt):
            print("-----------------------")
            print("Ingrese caracter valido")
            print("-----------------------")
            continue

        if opcion == 1:
            try:
                nombre = input("Ingrese el nombre de la persona: ")
            except (ValueError, KeyboardInterrupt):
                print("-----------------------")
                print("Ingrese caracter valido")
                print("-----------------------") 
                continue
            try:
                edad = int(input("Ingrese la edad de la persona: "))
            except (ValueError, KeyboardInterrupt):
                print("-----------------------")
                print("Ingrese caracter valido")
                print("-----------------------")
                continue
            personas.append(Persona(nombre, edad))
            print("Persona agregada con exito.")
            time.sleep(1)

        elif opcion == 2:
            if not personas:
                print("-------------------------------")
                print("No hay personas que listar.")
                print("-------------------------------")
            else:
                print("Lista de personas:")
                for i, persona in enumerate(personas, start=1): #i guarda el numero del listado y persona guarda los datos de la persona dentro de la lista
                    print(f"{i}. {persona.nombre} - {persona.edad} años")

        elif opcion == 3:
            if not personas:
                print("-------------------------------")
                print("No hay personas que modificar.")
                print("-------------------------------")
            else:
                print("Lista de personas para modificar:")
                for i, persona in enumerate(personas, start=1):  #i guarda el numero del listado y persona guarda los datos de la persona dentro de la lista
                    print(f"{i}. {persona.nombre} - {persona.edad} años")
                try:
                    opcion = int(input("Por favor seleccione una persona para modificar: "))
                except (ValueError, KeyboardInterrupt):
                    print("-----------------------")
                    print("Ingrese caracter valido")
                    print("-----------------------")
                    continue
                try:
                    nuevo_nombre = input("Por favor escriba el nuevo nombre: ")
                except (ValueError, KeyboardInterrupt):
                    print("-----------------------")
                    print("Ingrese caracter valido")
                    print("-----------------------")
                    continue
                try:
                    nueva_edad = int(input("Por favor ingrese nueva edad: "))
                except (ValueError, KeyboardInterrupt):
                    print("-----------------------")
                    print("Ingrese caracter valido")
                    print("-----------------------")
                    continue
                personas[opcion - 1].modificar(nuevo_nombre, nueva_edad)
                print("Persona modificada con exito.")
                time.sleep(1)

        elif opcion == 4:
            if not personas:
                print("-------------------------------")
                print("No hay personas que quitar.")
                print("-------------------------------")
            else:
                print("Lista de personas para quitar:")
                for i, persona in enumerate(personas, start=1):  #i guarda el numero del listado y persona guarda los datos de la persona
                    print(f"{i}. {persona.nombre} - {persona.edad} años")
                try:
                    opcion = int(input("Por favor seleccione una persona para quitar: "))
                except (ValueError, KeyboardInterrupt):
                    print("-----------------------")
                    print("Ingrese caracter valido")
                    print("-----------------------")
                    continue
                del personas[opcion - 1]
                print("Persona Eliminada con exito.")
                time.sleep(1)

        elif opcion == 5:
            print("Volviendo al menu principal.")
            time.sleep(1)
            return


def gestiontareas():  # funcion de gestion de tareas
    while True:  # se reiniciara hasta escoger una opcion valida
        print("Entraste a gestion de tareas")
        print("-------------------------------")
        print("1.- Agregar tarea")
        print("2.- Listar tareas")
        print("3.- Modificar tarea")
        print("4.- Quitar tarea")
        print("5.- Volver al menu principal")
        print("-------------------------------")
        try:
            opcion = int(input("Por favor seleccione una opcion: "))
        except (ValueError, KeyboardInterrupt):
            print("-----------------------")
            print("Ingrese caracter valido")
            print("-----------------------")
            continue

        if opcion == 1:
            while True:
                try:
                    nombre_tarea = input("Ingrese el nombre de la tarea: ")
                except (ValueError, KeyboardInterrupt):
                    print("-----------------------")
                    print("Ingrese caracter valido")
                    print("-----------------------")
                    continue
                try:
                    nivel_tarea = int(input("Ingrese el nivel de dificultad (1.- Bajo | 2.- Medio | 3.- Dificil ): "))
                except (ValueError, KeyboardInterrupt):
                    print("-----------------------")
                    print("Ingrese caracter valido")
                    print("-----------------------")
                    continue
                try:
                    hora_tarea = input("Ingrese la hora para comenzar la tarea (HH:MM): ")
                except (ValueError, KeyboardInterrupt):
                    print("-----------------------")
                    print("Ingrese caracter valido")
                    print("-----------------------")
                    continue

                if ":" in hora_tarea:
                    tareas.append(Tarea(nombre_tarea, nivel_tarea, hora_tarea))
                    print("Tarea agregada con exito.")
                    time.sleep(1)
                    break
                else:
                    print("Formato de hora incorrecto. Use HH:MM. ")
                    time.sleep(1)

        if opcion == 2:
            if not tareas:
                print("-------------------------------")
                print("No hay personas que listar.")
                print("-------------------------------")
            else:
                print("Lista de tareas:")
                for i, tarea in enumerate(tareas, start=1):
                    print(f"{i}. {tarea.nombre} | Dificultad: {tarea.nivel} | Hora: {tarea.hora}")

        if opcion == 3:
            if not tareas:
                print("-------------------------------")
                print("No hay personas que eliminar.")
                print("-------------------------------")
            else:
                print("Lista de tareas:")
                for i, tarea in enumerate(tareas, start=1):
                    print(f"{i}. {tarea.nombre} | Dificultad: {tarea.nivel} | Hora: {tarea.hora}")
                try:
                    opcion = int(input("Por favor seleccione una tarea para modificar: "))
                except (ValueError, KeyboardInterrupt):
                    print("-----------------------")
                    print("Ingrese caracter valido")
                    print("-----------------------")
                    continue
                try:
                    nuevo_nombre = int(input("Nuevo nombre de la tarea: "))
                except (ValueError, KeyboardInterrupt):
                    print("-----------------------")
                    print("Ingrese caracter valido")
                    print("-----------------------")
                    continue
                try:
                    nuevo_nivel = input("Nuevo nivel de dificultad de la tarea (1.- Bajo | 2.- Medio | 3.- Dificil ): ")
                except (ValueError, KeyboardInterrupt):
                    print("-----------------------")
                    print("Ingrese caracter valido")
                    print("-----------------------")
                    continue
                try:
                    nueva_hora = input("Nueva hora de la tarea (HH:MM): ")
                except (ValueError, KeyboardInterrupt):
                    print("-----------------------")
                    print("Ingrese caracter valido")
                    print("-----------------------")
                    continue

                tareas[opcion - 1].nombre = nuevo_nombre
                tareas[opcion - 1].nivel = nuevo_nivel
                tareas[opcion - 1].hora = nueva_hora

                print("Tarea modificada con exito.")
                time.sleep(1)

        if opcion == 4:
            if not tareas:
                print("-------------------------------")
                print("No hay personas que eliminar.")
                print("-------------------------------")
            else:
                print("Lista de tareas:")
                for i, tarea in enumerate(tareas, start=1):
                    print(f"{i}. {tarea.nombre} | Dificultad: {tarea.nivel} | Hora: {tarea.hora}")
                try:
                    opcion = int(input("Por favor seleccione una tarea para quitar: "))
                except (ValueError, KeyboardInterrupt):
                    print("-----------------------")
                    print("Ingrese caracter valido")
                    print("-----------------------")
                    continue
                del tareas[opcion - 1]
                print("Tarea Eliminada con exito.")
                time.sleep(1)

        elif opcion == 5:
            print("Volviendo al menu principal.")
            time.sleep(1)
            return


def asignaciones():
    while True:
        print("Entraste a Asignaciones")
        print("-------------------------------")
        print("1.- Asignar tareas aleatoriamente")
        print("2.- Listar asignaciones actuales")
        print("3.- Volver al menú principal")
        print("-------------------------------")

        try:
            opcion = int(input("Por favor seleccione una opción: "))
        except (ValueError, KeyboardInterrupt):
            print("Ingrese carácter válido")
            continue

        if opcion == 1:
            if len(tareas) > len(personas):
                print("Hay más tareas que personas, ¿deseas continuar?")
                print("1.- Sí")
                print("2.- No")

                try:
                    opcion = int(input("Seleccione una opción: "))
                except (ValueError, KeyboardInterrupt):
                    print("Ingrese carácter válido")
                    continue

                if opcion == 2:
                    print("Regresando al menú...")
                    time.sleep(1)
                    return  

            personas_disponibles = personas.copy()

            # Asignar una tarea a cada persona
            for tarea in tareas:
                if not personas_disponibles:
                    personas_disponibles = personas.copy()  # Vuelve a usar todas las personas
                    random.shuffle(personas_disponibles)

                persona_asignada = personas_disponibles.pop()  
                asignaciones_guardadas.append((persona_asignada, tarea))
                random.shuffle(personas_disponibles)

            print("Asignaciones completadas con éxito.")
            time.sleep(1)

        elif opcion == 2:
            if not asignaciones_guardadas:
                print("No hay asignaciones.")
            else:
                print("Lista de asignaciones:")
                for i, (persona, tarea) in enumerate(asignaciones_guardadas, start=1):
                    print(f"{i}. {tarea.nombre} | Dificultad: {tarea.nivel} | Hora: {tarea.hora} asignada a {persona.nombre}")

        elif opcion == 3:
            print("Volviendo al menú principal.")
            time.sleep(1)
            return


login()
