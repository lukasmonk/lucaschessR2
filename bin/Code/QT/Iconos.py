from PySide2 import QtGui

import Code

f = open(Code.path_resource("IntFiles", "Iconos.bin"), "rb")
binIconos = f.read()
f.close()


def icono(name):
    return eval("%s()" % name)


def pixmap(name):
    return eval("pm%s()" % name)


def PM(desde, hasta):
    pm = QtGui.QPixmap()
    pm.loadFromData(binIconos[desde:hasta])
    return pm


def pmLM():
    return PM(0, 1248)


def LM():
    return QtGui.QIcon(pmLM())


def pmAplicacion64():
    return PM(1248, 6430)


def Aplicacion64():
    return QtGui.QIcon(pmAplicacion64())


def pmDatos():
    return PM(6430, 7617)


def Datos():
    return QtGui.QIcon(pmDatos())


def pmTutor():
    return PM(7617, 9646)


def Tutor():
    return QtGui.QIcon(pmTutor())


def pmPartidaOriginal():
    return PM(9646, 11623)


def PartidaOriginal():
    return QtGui.QIcon(pmPartidaOriginal())


def pmFindAllMoves():
    return PM(11623, 13219)


def FindAllMoves():
    return QtGui.QIcon(pmFindAllMoves())


def pmResizeBoard():
    return PM(11623, 13219)


def ResizeBoard():
    return QtGui.QIcon(pmResizeBoard())


def pmMensEspera():
    return PM(13219, 16967)


def MensEspera():
    return QtGui.QIcon(pmMensEspera())


def pmUtilidades():
    return PM(16967, 23396)


def Utilidades():
    return QtGui.QIcon(pmUtilidades())


def pmTerminar():
    return PM(23396, 25146)


def Terminar():
    return QtGui.QIcon(pmTerminar())


def pmNuevaPartida():
    return PM(25146, 26894)


def NuevaPartida():
    return QtGui.QIcon(pmNuevaPartida())


def pmOpciones():
    return PM(26894, 28622)


def Opciones():
    return QtGui.QIcon(pmOpciones())


def pmEntrenamiento():
    return PM(7617, 9646)


def Entrenamiento():
    return QtGui.QIcon(pmEntrenamiento())


def pmAplazar():
    return PM(28622, 31689)


def Aplazar():
    return QtGui.QIcon(pmAplazar())


def pmAplazamientos():
    return PM(31689, 35005)


def Aplazamientos():
    return QtGui.QIcon(pmAplazamientos())


def pmCapturas():
    return PM(35005, 37046)


def Capturas():
    return QtGui.QIcon(pmCapturas())


def pmReiniciar():
    return PM(37046, 39340)


def Reiniciar():
    return QtGui.QIcon(pmReiniciar())


def pmImportarGM():
    return PM(39340, 41940)


def ImportarGM():
    return QtGui.QIcon(pmImportarGM())


def pmAbandonar():
    return PM(41940, 45940)


def Abandonar():
    return QtGui.QIcon(pmAbandonar())


def pmEmpezar():
    return PM(45940, 47976)


def Empezar():
    return QtGui.QIcon(pmEmpezar())


def pmOtros():
    return PM(47976, 52446)


def Otros():
    return QtGui.QIcon(pmOtros())


def pmAnalizar():
    return PM(52446, 53983)


def Analizar():
    return QtGui.QIcon(pmAnalizar())


def pmMainMenu():
    return PM(53983, 58293)


def MainMenu():
    return QtGui.QIcon(pmMainMenu())


def pmFinPartida():
    return PM(58293, 61241)


def FinPartida():
    return QtGui.QIcon(pmFinPartida())


def pmGrabar():
    return PM(61241, 62704)


def Grabar():
    return QtGui.QIcon(pmGrabar())


def pmGrabarComo():
    return PM(62704, 64756)


def GrabarComo():
    return QtGui.QIcon(pmGrabarComo())


def pmRecuperar():
    return PM(64756, 67514)


def Recuperar():
    return QtGui.QIcon(pmRecuperar())


def pmInformacion():
    return PM(67514, 69473)


def Informacion():
    return QtGui.QIcon(pmInformacion())


def pmNuevo():
    return PM(69473, 70227)


def Nuevo():
    return QtGui.QIcon(pmNuevo())


def pmCopiar():
    return PM(70227, 71408)


def Copiar():
    return QtGui.QIcon(pmCopiar())


def pmModificar():
    return PM(71408, 75805)


def Modificar():
    return QtGui.QIcon(pmModificar())


def pmBorrar():
    return PM(75805, 80796)


def Borrar():
    return QtGui.QIcon(pmBorrar())


def pmMarcar():
    return PM(80796, 85725)


def Marcar():
    return QtGui.QIcon(pmMarcar())


def pmPegar():
    return PM(85725, 88036)


def Pegar():
    return QtGui.QIcon(pmPegar())


def pmFichero():
    return PM(88036, 92721)


def Fichero():
    return QtGui.QIcon(pmFichero())


def pmNuestroFichero():
    return PM(92721, 95768)


def NuestroFichero():
    return QtGui.QIcon(pmNuestroFichero())


def pmFicheroRepite():
    return PM(95768, 97264)


def FicheroRepite():
    return QtGui.QIcon(pmFicheroRepite())


def pmInformacionPGN():
    return PM(97264, 98282)


def InformacionPGN():
    return QtGui.QIcon(pmInformacionPGN())


def pmVer():
    return PM(98282, 99736)


def Ver():
    return QtGui.QIcon(pmVer())


def pmInicio():
    return PM(99736, 101750)


def Inicio():
    return QtGui.QIcon(pmInicio())


def pmFinal():
    return PM(101750, 103744)


def Final():
    return QtGui.QIcon(pmFinal())


def pmFiltrar():
    return PM(103744, 110234)


def Filtrar():
    return QtGui.QIcon(pmFiltrar())


def pmArriba():
    return PM(110234, 112387)


def Arriba():
    return QtGui.QIcon(pmArriba())


def pmAbajo():
    return PM(112387, 114495)


def Abajo():
    return QtGui.QIcon(pmAbajo())


def pmEstadisticas():
    return PM(114495, 116634)


def Estadisticas():
    return QtGui.QIcon(pmEstadisticas())


def pmCheck():
    return PM(116634, 119858)


def Check():
    return QtGui.QIcon(pmCheck())


def pmTablas():
    return PM(119858, 121481)


def Tablas():
    return QtGui.QIcon(pmTablas())


def pmAtras():
    return PM(121481, 123000)


def Atras():
    return QtGui.QIcon(pmAtras())


def pmBuscar():
    return PM(123000, 124985)


def Buscar():
    return QtGui.QIcon(pmBuscar())


def pmLibros():
    return PM(124985, 127113)


def Libros():
    return QtGui.QIcon(pmLibros())


def pmAceptar():
    return PM(127113, 130460)


def Aceptar():
    return QtGui.QIcon(pmAceptar())


def pmCancelar():
    return PM(130460, 132443)


def Cancelar():
    return QtGui.QIcon(pmCancelar())


def pmDefecto():
    return PM(132443, 135762)


def Defecto():
    return QtGui.QIcon(pmDefecto())


def pmInsertar():
    return PM(135762, 138158)


def Insertar():
    return QtGui.QIcon(pmInsertar())


def pmJugar():
    return PM(138158, 140367)


def Jugar():
    return QtGui.QIcon(pmJugar())


def pmConfigurar():
    return PM(140367, 143451)


def Configurar():
    return QtGui.QIcon(pmConfigurar())


def pmS_Aceptar():
    return PM(127113, 130460)


def S_Aceptar():
    return QtGui.QIcon(pmS_Aceptar())


def pmS_Cancelar():
    return PM(130460, 132443)


def S_Cancelar():
    return QtGui.QIcon(pmS_Cancelar())


def pmS_Microfono():
    return PM(143451, 148892)


def S_Microfono():
    return QtGui.QIcon(pmS_Microfono())


def pmS_LeerWav():
    return PM(39340, 41940)


def S_LeerWav():
    return QtGui.QIcon(pmS_LeerWav())


def pmS_Play():
    return PM(148892, 154230)


def S_Play():
    return QtGui.QIcon(pmS_Play())


def pmS_StopPlay():
    return PM(154230, 154840)


def S_StopPlay():
    return QtGui.QIcon(pmS_StopPlay())


def pmS_StopMicrofono():
    return PM(154230, 154840)


def S_StopMicrofono():
    return QtGui.QIcon(pmS_StopMicrofono())


def pmS_Record():
    return PM(154840, 158073)


def S_Record():
    return QtGui.QIcon(pmS_Record())


def pmS_Limpiar():
    return PM(75805, 80796)


def S_Limpiar():
    return QtGui.QIcon(pmS_Limpiar())


def pmHistorial():
    return PM(158073, 159336)


def Historial():
    return QtGui.QIcon(pmHistorial())


def pmPegar16():
    return PM(159336, 160330)


def Pegar16():
    return QtGui.QIcon(pmPegar16())


def pmRivalesMP():
    return PM(160330, 163012)


def RivalesMP():
    return QtGui.QIcon(pmRivalesMP())


def pmCamara():
    return PM(163012, 164534)


def Camara():
    return QtGui.QIcon(pmCamara())


def pmUsuarios():
    return PM(164534, 165774)


def Usuarios():
    return QtGui.QIcon(pmUsuarios())


def pmResistencia():
    return PM(165774, 168836)


def Resistencia():
    return QtGui.QIcon(pmResistencia())


def pmCebra():
    return PM(168836, 171289)


def Cebra():
    return QtGui.QIcon(pmCebra())


def pmGafas():
    return PM(171289, 172447)


def Gafas():
    return QtGui.QIcon(pmGafas())


def pmPuente():
    return PM(172447, 173083)


def Puente():
    return QtGui.QIcon(pmPuente())


def pmWeb():
    return PM(173083, 174265)


def Web():
    return QtGui.QIcon(pmWeb())


def pmMail():
    return PM(174265, 175225)


def Mail():
    return QtGui.QIcon(pmMail())


def pmAyuda():
    return PM(175225, 176406)


def Ayuda():
    return QtGui.QIcon(pmAyuda())


def pmFAQ():
    return PM(176406, 177727)


def FAQ():
    return QtGui.QIcon(pmFAQ())


def pmActualiza():
    return PM(177727, 178593)


def Actualiza():
    return QtGui.QIcon(pmActualiza())


def pmRefresh():
    return PM(178593, 180985)


def Refresh():
    return QtGui.QIcon(pmRefresh())


def pmJuegaSolo():
    return PM(180985, 182837)


def JuegaSolo():
    return QtGui.QIcon(pmJuegaSolo())


def pmPlayer():
    return PM(182837, 184019)


def Player():
    return QtGui.QIcon(pmPlayer())


def pmJS_Rotacion():
    return PM(184019, 185929)


def JS_Rotacion():
    return QtGui.QIcon(pmJS_Rotacion())


def pmElo():
    return PM(185929, 187435)


def Elo():
    return QtGui.QIcon(pmElo())


def pmMate():
    return PM(187435, 187996)


def Mate():
    return QtGui.QIcon(pmMate())


def pmEloTimed():
    return PM(187996, 189480)


def EloTimed():
    return QtGui.QIcon(pmEloTimed())


def pmPGN():
    return PM(189480, 191478)


def PGN():
    return QtGui.QIcon(pmPGN())


def pmPGN_Importar():
    return PM(191478, 193068)


def PGN_Importar():
    return QtGui.QIcon(pmPGN_Importar())


def pmAyudaGR():
    return PM(193068, 198946)


def AyudaGR():
    return QtGui.QIcon(pmAyudaGR())


def pmBotonAyuda():
    return PM(198946, 201406)


def BotonAyuda():
    return QtGui.QIcon(pmBotonAyuda())


def pmColores():
    return PM(201406, 202637)


def Colores():
    return QtGui.QIcon(pmColores())


def pmEditarColores():
    return PM(202637, 204940)


def EditarColores():
    return QtGui.QIcon(pmEditarColores())


def pmGranMaestro():
    return PM(204940, 205796)


def GranMaestro():
    return QtGui.QIcon(pmGranMaestro())


def pmFavoritos():
    return PM(205796, 207562)


def Favoritos():
    return QtGui.QIcon(pmFavoritos())


def pmCarpeta():
    return PM(207562, 208266)


def Carpeta():
    return QtGui.QIcon(pmCarpeta())


def pmDivision():
    return PM(208266, 208931)


def Division():
    return QtGui.QIcon(pmDivision())


def pmDivisionF():
    return PM(208931, 210045)


def DivisionF():
    return QtGui.QIcon(pmDivisionF())


def pmDelete():
    return PM(210045, 210969)


def Delete():
    return QtGui.QIcon(pmDelete())


def pmModificarP():
    return PM(210969, 212035)


def ModificarP():
    return QtGui.QIcon(pmModificarP())


def pmGrupo_Si():
    return PM(212035, 212497)


def Grupo_Si():
    return QtGui.QIcon(pmGrupo_Si())


def pmGrupo_No():
    return PM(212497, 212820)


def Grupo_No():
    return QtGui.QIcon(pmGrupo_No())


def pmMotor_Si():
    return PM(212820, 213282)


def Motor_Si():
    return QtGui.QIcon(pmMotor_Si())


def pmMotor_No():
    return PM(210045, 210969)


def Motor_No():
    return QtGui.QIcon(pmMotor_No())


def pmMotor_Actual():
    return PM(213282, 214299)


def Motor_Actual():
    return QtGui.QIcon(pmMotor_Actual())


def pmMoverInicio():
    return PM(214299, 214597)


def MoverInicio():
    return QtGui.QIcon(pmMoverInicio())


def pmMoverFinal():
    return PM(214597, 214898)


def MoverFinal():
    return QtGui.QIcon(pmMoverFinal())


def pmMoverAdelante():
    return PM(214898, 215253)


def MoverAdelante():
    return QtGui.QIcon(pmMoverAdelante())


def pmMoverAtras():
    return PM(215253, 215618)


def MoverAtras():
    return QtGui.QIcon(pmMoverAtras())


def pmMoverLibre():
    return PM(215618, 216036)


def MoverLibre():
    return QtGui.QIcon(pmMoverLibre())


def pmMoverTiempo():
    return PM(216036, 216615)


def MoverTiempo():
    return QtGui.QIcon(pmMoverTiempo())


def pmMoverMas():
    return PM(216615, 217654)


def MoverMas():
    return QtGui.QIcon(pmMoverMas())


def pmMoverGrabar():
    return PM(217654, 218510)


def MoverGrabar():
    return QtGui.QIcon(pmMoverGrabar())


def pmMoverGrabarTodos():
    return PM(218510, 219554)


def MoverGrabarTodos():
    return QtGui.QIcon(pmMoverGrabarTodos())


def pmMoverJugar():
    return PM(219554, 220385)


def MoverJugar():
    return QtGui.QIcon(pmMoverJugar())


def pmPelicula():
    return PM(220385, 222519)


def Pelicula():
    return QtGui.QIcon(pmPelicula())


def pmPelicula_Pausa():
    return PM(222519, 224278)


def Pelicula_Pausa():
    return QtGui.QIcon(pmPelicula_Pausa())


def pmPelicula_Seguir():
    return PM(224278, 226367)


def Pelicula_Seguir():
    return QtGui.QIcon(pmPelicula_Seguir())


def pmPelicula_Rapido():
    return PM(226367, 228426)


def Pelicula_Rapido():
    return QtGui.QIcon(pmPelicula_Rapido())


def pmPelicula_Lento():
    return PM(228426, 230301)


def Pelicula_Lento():
    return QtGui.QIcon(pmPelicula_Lento())


def pmPelicula_Repetir():
    return PM(37046, 39340)


def Pelicula_Repetir():
    return QtGui.QIcon(pmPelicula_Repetir())


def pmPelicula_PGN():
    return PM(230301, 231209)


def Pelicula_PGN():
    return QtGui.QIcon(pmPelicula_PGN())


def pmMemoria():
    return PM(231209, 233150)


def Memoria():
    return QtGui.QIcon(pmMemoria())


def pmEntrenar():
    return PM(233150, 234689)


def Entrenar():
    return QtGui.QIcon(pmEntrenar())


def pmEnviar():
    return PM(233150, 234689)


def Enviar():
    return QtGui.QIcon(pmEnviar())


def pmBoxRooms():
    return PM(234689, 239492)


def BoxRooms():
    return QtGui.QIcon(pmBoxRooms())


def pmBoxRoom():
    return PM(239492, 239954)


def BoxRoom():
    return QtGui.QIcon(pmBoxRoom())


def pmNewBoxRoom():
    return PM(239954, 241462)


def NewBoxRoom():
    return QtGui.QIcon(pmNewBoxRoom())


def pmNuevoMas():
    return PM(239954, 241462)


def NuevoMas():
    return QtGui.QIcon(pmNuevoMas())


def pmTemas():
    return PM(241462, 243685)


def Temas():
    return QtGui.QIcon(pmTemas())


def pmTutorialesCrear():
    return PM(243685, 249954)


def TutorialesCrear():
    return QtGui.QIcon(pmTutorialesCrear())


def pmMover():
    return PM(249954, 250536)


def Mover():
    return QtGui.QIcon(pmMover())


def pmSeleccionar():
    return PM(250536, 256240)


def Seleccionar():
    return QtGui.QIcon(pmSeleccionar())


def pmVista():
    return PM(256240, 258164)


def Vista():
    return QtGui.QIcon(pmVista())


def pmInformacionPGNUno():
    return PM(258164, 259542)


def InformacionPGNUno():
    return QtGui.QIcon(pmInformacionPGNUno())


def pmDailyTest():
    return PM(259542, 261882)


def DailyTest():
    return QtGui.QIcon(pmDailyTest())


def pmJuegaPorMi():
    return PM(261882, 263602)


def JuegaPorMi():
    return QtGui.QIcon(pmJuegaPorMi())


def pmArbol():
    return PM(263602, 264236)


def Arbol():
    return QtGui.QIcon(pmArbol())


def pmGrabarFichero():
    return PM(61241, 62704)


def GrabarFichero():
    return QtGui.QIcon(pmGrabarFichero())


def pmClipboard():
    return PM(264236, 265014)


def Clipboard():
    return QtGui.QIcon(pmClipboard())


def pmFics():
    return PM(265014, 265431)


def Fics():
    return QtGui.QIcon(pmFics())


def pmFide():
    return PM(9646, 11623)


def Fide():
    return QtGui.QIcon(pmFide())


def pmFichPGN():
    return PM(25146, 26894)


def FichPGN():
    return QtGui.QIcon(pmFichPGN())


def pmFlechas():
    return PM(265431, 268783)


def Flechas():
    return QtGui.QIcon(pmFlechas())


def pmMarcos():
    return PM(268783, 270230)


def Marcos():
    return QtGui.QIcon(pmMarcos())


def pmSVGs():
    return PM(270230, 273799)


def SVGs():
    return QtGui.QIcon(pmSVGs())


def pmAmarillo():
    return PM(273799, 275051)


def Amarillo():
    return QtGui.QIcon(pmAmarillo())


def pmNaranja():
    return PM(275051, 276283)


def Naranja():
    return QtGui.QIcon(pmNaranja())


def pmVerde():
    return PM(276283, 277559)


def Verde():
    return QtGui.QIcon(pmVerde())


def pmAzul():
    return PM(277559, 278647)


def Azul():
    return QtGui.QIcon(pmAzul())


def pmMagenta():
    return PM(278647, 279935)


def Magenta():
    return QtGui.QIcon(pmMagenta())


def pmRojo():
    return PM(279935, 281154)


def Rojo():
    return QtGui.QIcon(pmRojo())


def pmGris():
    return PM(281154, 282112)


def Gris():
    return QtGui.QIcon(pmGris())


def pmAmarillo32():
    return PM(282112, 284092)


def Amarillo32():
    return QtGui.QIcon(pmAmarillo32())


def pmNaranja32():
    return PM(284092, 286216)


def Naranja32():
    return QtGui.QIcon(pmNaranja32())


def pmVerde32():
    return PM(286216, 288337)


def Verde32():
    return QtGui.QIcon(pmVerde32())


def pmAzul32():
    return PM(288337, 290716)


def Azul32():
    return QtGui.QIcon(pmAzul32())


def pmMagenta32():
    return PM(290716, 293167)


def Magenta32():
    return QtGui.QIcon(pmMagenta32())


def pmRojo32():
    return PM(293167, 294982)


def Rojo32():
    return QtGui.QIcon(pmRojo32())


def pmGris32():
    return PM(294982, 296896)


def Gris32():
    return QtGui.QIcon(pmGris32())


def pmPuntoBlanco():
    return PM(296896, 297245)


def PuntoBlanco():
    return QtGui.QIcon(pmPuntoBlanco())


def pmPuntoAmarillo():
    return PM(212035, 212497)


def PuntoAmarillo():
    return QtGui.QIcon(pmPuntoAmarillo())


def pmPuntoNaranja():
    return PM(297245, 297707)


def PuntoNaranja():
    return QtGui.QIcon(pmPuntoNaranja())


def pmPuntoVerde():
    return PM(212820, 213282)


def PuntoVerde():
    return QtGui.QIcon(pmPuntoVerde())


def pmPuntoAzul():
    return PM(239492, 239954)


def PuntoAzul():
    return QtGui.QIcon(pmPuntoAzul())


def pmPuntoMagenta():
    return PM(297707, 298206)


def PuntoMagenta():
    return QtGui.QIcon(pmPuntoMagenta())


def pmPuntoRojo():
    return PM(298206, 298705)


def PuntoRojo():
    return QtGui.QIcon(pmPuntoRojo())


def pmPuntoNegro():
    return PM(212497, 212820)


def PuntoNegro():
    return QtGui.QIcon(pmPuntoNegro())


def pmPuntoEstrella():
    return PM(298705, 299132)


def PuntoEstrella():
    return QtGui.QIcon(pmPuntoEstrella())


def pmComentario():
    return PM(299132, 299769)


def Comentario():
    return QtGui.QIcon(pmComentario())


def pmComentarioMas():
    return PM(299769, 300708)


def ComentarioMas():
    return QtGui.QIcon(pmComentarioMas())


def pmComentarioEditar():
    return PM(217654, 218510)


def ComentarioEditar():
    return QtGui.QIcon(pmComentarioEditar())


def pmOpeningComentario():
    return PM(300708, 301704)


def OpeningComentario():
    return QtGui.QIcon(pmOpeningComentario())


def pmMas():
    return PM(301704, 302213)


def Mas():
    return QtGui.QIcon(pmMas())


def pmMasR():
    return PM(302213, 302701)


def MasR():
    return QtGui.QIcon(pmMasR())


def pmMasDoc():
    return PM(302701, 303502)


def MasDoc():
    return QtGui.QIcon(pmMasDoc())


def pmPotencia():
    return PM(177727, 178593)


def Potencia():
    return QtGui.QIcon(pmPotencia())


def pmBMT():
    return PM(303502, 304380)


def BMT():
    return QtGui.QIcon(pmBMT())


def pmOjo():
    return PM(304380, 305502)


def Ojo():
    return QtGui.QIcon(pmOjo())


def pmOcultar():
    return PM(304380, 305502)


def Ocultar():
    return QtGui.QIcon(pmOcultar())


def pmMostrar():
    return PM(305502, 306558)


def Mostrar():
    return QtGui.QIcon(pmMostrar())


def pmBlog():
    return PM(306558, 307080)


def Blog():
    return QtGui.QIcon(pmBlog())


def pmVariations():
    return PM(307080, 307987)


def Variations():
    return QtGui.QIcon(pmVariations())


def pmVariationsG():
    return PM(307987, 310414)


def VariationsG():
    return QtGui.QIcon(pmVariationsG())


def pmCambiar():
    return PM(310414, 312128)


def Cambiar():
    return QtGui.QIcon(pmCambiar())


def pmAnterior():
    return PM(312128, 314182)


def Anterior():
    return QtGui.QIcon(pmAnterior())


def pmSiguiente():
    return PM(314182, 316252)


def Siguiente():
    return QtGui.QIcon(pmSiguiente())


def pmSiguienteF():
    return PM(316252, 318427)


def SiguienteF():
    return QtGui.QIcon(pmSiguienteF())


def pmAnteriorF():
    return PM(318427, 320621)


def AnteriorF():
    return QtGui.QIcon(pmAnteriorF())


def pmX():
    return PM(320621, 321903)


def X():
    return QtGui.QIcon(pmX())


def pmTools():
    return PM(321903, 324504)


def Tools():
    return QtGui.QIcon(pmTools())


def pmTacticas():
    return PM(324504, 327077)


def Tacticas():
    return QtGui.QIcon(pmTacticas())


def pmCancelarPeque():
    return PM(327077, 327639)


def CancelarPeque():
    return QtGui.QIcon(pmCancelarPeque())


def pmAceptarPeque():
    return PM(213282, 214299)


def AceptarPeque():
    return QtGui.QIcon(pmAceptarPeque())


def pmLibre():
    return PM(327639, 330031)


def Libre():
    return QtGui.QIcon(pmLibre())


def pmEnBlanco():
    return PM(330031, 330757)


def EnBlanco():
    return QtGui.QIcon(pmEnBlanco())


def pmDirector():
    return PM(330757, 333731)


def Director():
    return QtGui.QIcon(pmDirector())


def pmTorneos():
    return PM(333731, 335469)


def Torneos():
    return QtGui.QIcon(pmTorneos())


def pmOpenings():
    return PM(335469, 336394)


def Openings():
    return QtGui.QIcon(pmOpenings())


def pmV_Blancas():
    return PM(336394, 336674)


def V_Blancas():
    return QtGui.QIcon(pmV_Blancas())


def pmV_Blancas_Mas():
    return PM(336674, 336954)


def V_Blancas_Mas():
    return QtGui.QIcon(pmV_Blancas_Mas())


def pmV_Blancas_Mas_Mas():
    return PM(336954, 337226)


def V_Blancas_Mas_Mas():
    return QtGui.QIcon(pmV_Blancas_Mas_Mas())


def pmV_Negras():
    return PM(337226, 337501)


def V_Negras():
    return QtGui.QIcon(pmV_Negras())


def pmV_Negras_Mas():
    return PM(337501, 337776)


def V_Negras_Mas():
    return QtGui.QIcon(pmV_Negras_Mas())


def pmV_Negras_Mas_Mas():
    return PM(337776, 338045)


def V_Negras_Mas_Mas():
    return QtGui.QIcon(pmV_Negras_Mas_Mas())


def pmV_Blancas_Igual_Negras():
    return PM(338045, 338347)


def V_Blancas_Igual_Negras():
    return QtGui.QIcon(pmV_Blancas_Igual_Negras())


def pmMezclar():
    return PM(135762, 138158)


def Mezclar():
    return QtGui.QIcon(pmMezclar())


def pmVoyager():
    return PM(338347, 339190)


def Voyager():
    return QtGui.QIcon(pmVoyager())


def pmVoyager32():
    return PM(339190, 341078)


def Voyager32():
    return QtGui.QIcon(pmVoyager32())


def pmReindexar():
    return PM(341078, 342895)


def Reindexar():
    return QtGui.QIcon(pmReindexar())


def pmRename():
    return PM(342895, 343879)


def Rename():
    return QtGui.QIcon(pmRename())


def pmAdd():
    return PM(343879, 344832)


def Add():
    return QtGui.QIcon(pmAdd())


def pmMas22():
    return PM(344832, 345496)


def Mas22():
    return QtGui.QIcon(pmMas22())


def pmMenos22():
    return PM(345496, 345940)


def Menos22():
    return QtGui.QIcon(pmMenos22())


def pmTransposition():
    return PM(345940, 346459)


def Transposition():
    return QtGui.QIcon(pmTransposition())


def pmRat():
    return PM(346459, 352163)


def Rat():
    return QtGui.QIcon(pmRat())


def pmAlligator():
    return PM(352163, 357155)


def Alligator():
    return QtGui.QIcon(pmAlligator())


def pmAnt():
    return PM(357155, 363853)


def Ant():
    return QtGui.QIcon(pmAnt())


def pmBat():
    return PM(363853, 366807)


def Bat():
    return QtGui.QIcon(pmBat())


def pmBear():
    return PM(366807, 374086)


def Bear():
    return QtGui.QIcon(pmBear())


def pmBee():
    return PM(374086, 379088)


def Bee():
    return QtGui.QIcon(pmBee())


def pmBird():
    return PM(379088, 385147)


def Bird():
    return QtGui.QIcon(pmBird())


def pmBull():
    return PM(385147, 392116)


def Bull():
    return QtGui.QIcon(pmBull())


def pmBulldog():
    return PM(392116, 399007)


def Bulldog():
    return QtGui.QIcon(pmBulldog())


def pmButterfly():
    return PM(399007, 406381)


def Butterfly():
    return QtGui.QIcon(pmButterfly())


def pmCat():
    return PM(406381, 412653)


def Cat():
    return QtGui.QIcon(pmCat())


def pmChicken():
    return PM(412653, 418464)


def Chicken():
    return QtGui.QIcon(pmChicken())


def pmCow():
    return PM(418464, 425207)


def Cow():
    return QtGui.QIcon(pmCow())


def pmCrab():
    return PM(425207, 430796)


def Crab():
    return QtGui.QIcon(pmCrab())


def pmCrocodile():
    return PM(430796, 436937)


def Crocodile():
    return QtGui.QIcon(pmCrocodile())


def pmDeer():
    return PM(436937, 443244)


def Deer():
    return QtGui.QIcon(pmDeer())


def pmDog():
    return PM(443244, 449847)


def Dog():
    return QtGui.QIcon(pmDog())


def pmDonkey():
    return PM(449847, 455494)


def Donkey():
    return QtGui.QIcon(pmDonkey())


def pmDuck():
    return PM(455494, 462037)


def Duck():
    return QtGui.QIcon(pmDuck())


def pmEagle():
    return PM(462037, 466855)


def Eagle():
    return QtGui.QIcon(pmEagle())


def pmElephant():
    return PM(466855, 473336)


def Elephant():
    return QtGui.QIcon(pmElephant())


def pmFish():
    return PM(473336, 480177)


def Fish():
    return QtGui.QIcon(pmFish())


def pmFox():
    return PM(480177, 486960)


def Fox():
    return QtGui.QIcon(pmFox())


def pmFrog():
    return PM(486960, 493376)


def Frog():
    return QtGui.QIcon(pmFrog())


def pmGiraffe():
    return PM(493376, 500554)


def Giraffe():
    return QtGui.QIcon(pmGiraffe())


def pmGorilla():
    return PM(500554, 507093)


def Gorilla():
    return QtGui.QIcon(pmGorilla())


def pmHippo():
    return PM(507093, 514214)


def Hippo():
    return QtGui.QIcon(pmHippo())


def pmHorse():
    return PM(514214, 520761)


def Horse():
    return QtGui.QIcon(pmHorse())


def pmInsect():
    return PM(520761, 526696)


def Insect():
    return QtGui.QIcon(pmInsect())


def pmLion():
    return PM(526696, 535606)


def Lion():
    return QtGui.QIcon(pmLion())


def pmMonkey():
    return PM(535606, 543285)


def Monkey():
    return QtGui.QIcon(pmMonkey())


def pmMoose():
    return PM(543285, 549909)


def Moose():
    return QtGui.QIcon(pmMoose())


def pmMouse():
    return PM(346459, 352163)


def Mouse():
    return QtGui.QIcon(pmMouse())


def pmOwl():
    return PM(549909, 556615)


def Owl():
    return QtGui.QIcon(pmOwl())


def pmPanda():
    return PM(556615, 560649)


def Panda():
    return QtGui.QIcon(pmPanda())


def pmPenguin():
    return PM(560649, 566198)


def Penguin():
    return QtGui.QIcon(pmPenguin())


def pmPig():
    return PM(566198, 574238)


def Pig():
    return QtGui.QIcon(pmPig())


def pmRabbit():
    return PM(574238, 581539)


def Rabbit():
    return QtGui.QIcon(pmRabbit())


def pmRhino():
    return PM(581539, 587926)


def Rhino():
    return QtGui.QIcon(pmRhino())


def pmRooster():
    return PM(587926, 593189)


def Rooster():
    return QtGui.QIcon(pmRooster())


def pmShark():
    return PM(593189, 598959)


def Shark():
    return QtGui.QIcon(pmShark())


def pmSheep():
    return PM(598959, 602790)


def Sheep():
    return QtGui.QIcon(pmSheep())


def pmSnake():
    return PM(602790, 608815)


def Snake():
    return QtGui.QIcon(pmSnake())


def pmTiger():
    return PM(608815, 616852)


def Tiger():
    return QtGui.QIcon(pmTiger())


def pmTurkey():
    return PM(616852, 624266)


def Turkey():
    return QtGui.QIcon(pmTurkey())


def pmTurtle():
    return PM(624266, 630987)


def Turtle():
    return QtGui.QIcon(pmTurtle())


def pmWolf():
    return PM(630987, 634082)


def Wolf():
    return QtGui.QIcon(pmWolf())


def pmSteven():
    return PM(634082, 637742)


def Steven():
    return QtGui.QIcon(pmSteven())


def pmKnightMan():
    return PM(637742, 644894)


def KnightMan():
    return QtGui.QIcon(pmKnightMan())


def pmWheel():
    return PM(644894, 652959)


def Wheel():
    return QtGui.QIcon(pmWheel())


def pmWheelchair():
    return PM(652959, 661763)


def Wheelchair():
    return QtGui.QIcon(pmWheelchair())


def pmTouringMotorcycle():
    return PM(661763, 668075)


def TouringMotorcycle():
    return QtGui.QIcon(pmTouringMotorcycle())


def pmContainer():
    return PM(668075, 673410)


def Container():
    return QtGui.QIcon(pmContainer())


def pmBoatEquipment():
    return PM(673410, 678933)


def BoatEquipment():
    return QtGui.QIcon(pmBoatEquipment())


def pmCar():
    return PM(678933, 683579)


def Car():
    return QtGui.QIcon(pmCar())


def pmLorry():
    return PM(683579, 689615)


def Lorry():
    return QtGui.QIcon(pmLorry())


def pmCarTrailer():
    return PM(689615, 693712)


def CarTrailer():
    return QtGui.QIcon(pmCarTrailer())


def pmTowTruck():
    return PM(693712, 698470)


def TowTruck():
    return QtGui.QIcon(pmTowTruck())


def pmQuadBike():
    return PM(698470, 704439)


def QuadBike():
    return QtGui.QIcon(pmQuadBike())


def pmRecoveryTruck():
    return PM(704439, 709436)


def RecoveryTruck():
    return QtGui.QIcon(pmRecoveryTruck())


def pmContainerLoader():
    return PM(709436, 714578)


def ContainerLoader():
    return QtGui.QIcon(pmContainerLoader())


def pmPoliceCar():
    return PM(714578, 719410)


def PoliceCar():
    return QtGui.QIcon(pmPoliceCar())


def pmExecutiveCar():
    return PM(719410, 724088)


def ExecutiveCar():
    return QtGui.QIcon(pmExecutiveCar())


def pmTruck():
    return PM(724088, 729551)


def Truck():
    return QtGui.QIcon(pmTruck())


def pmExcavator():
    return PM(729551, 734442)


def Excavator():
    return QtGui.QIcon(pmExcavator())


def pmCabriolet():
    return PM(734442, 739280)


def Cabriolet():
    return QtGui.QIcon(pmCabriolet())


def pmMixerTruck():
    return PM(739280, 745590)


def MixerTruck():
    return QtGui.QIcon(pmMixerTruck())


def pmForkliftTruckLoaded():
    return PM(745590, 751738)


def ForkliftTruckLoaded():
    return QtGui.QIcon(pmForkliftTruckLoaded())


def pmAmbulance():
    return PM(751738, 757788)


def Ambulance():
    return QtGui.QIcon(pmAmbulance())


def pmDieselLocomotiveBoxcar():
    return PM(757788, 761794)


def DieselLocomotiveBoxcar():
    return QtGui.QIcon(pmDieselLocomotiveBoxcar())


def pmTractorUnit():
    return PM(761794, 767261)


def TractorUnit():
    return QtGui.QIcon(pmTractorUnit())


def pmFireTruck():
    return PM(767261, 773600)


def FireTruck():
    return QtGui.QIcon(pmFireTruck())


def pmCargoShip():
    return PM(773600, 777941)


def CargoShip():
    return QtGui.QIcon(pmCargoShip())


def pmSubwayTrain():
    return PM(777941, 782831)


def SubwayTrain():
    return QtGui.QIcon(pmSubwayTrain())


def pmTruckMountedCrane():
    return PM(782831, 788572)


def TruckMountedCrane():
    return QtGui.QIcon(pmTruckMountedCrane())


def pmAirAmbulance():
    return PM(788572, 793685)


def AirAmbulance():
    return QtGui.QIcon(pmAirAmbulance())


def pmAirplane():
    return PM(793685, 798573)


def Airplane():
    return QtGui.QIcon(pmAirplane())


def pmCaracol():
    return PM(798573, 800389)


def Caracol():
    return QtGui.QIcon(pmCaracol())


def pmUno():
    return PM(800389, 802851)


def Uno():
    return QtGui.QIcon(pmUno())


def pmMotoresExternos():
    return PM(802851, 804753)


def MotoresExternos():
    return QtGui.QIcon(pmMotoresExternos())


def pmDatabase():
    return PM(804753, 806069)


def Database():
    return QtGui.QIcon(pmDatabase())


def pmDatabaseMas():
    return PM(806069, 807528)


def DatabaseMas():
    return QtGui.QIcon(pmDatabaseMas())


def pmDatabaseImport():
    return PM(807528, 808164)


def DatabaseImport():
    return QtGui.QIcon(pmDatabaseImport())


def pmDatabaseExport():
    return PM(808164, 808809)


def DatabaseExport():
    return QtGui.QIcon(pmDatabaseExport())


def pmDatabaseDelete():
    return PM(808809, 809932)


def DatabaseDelete():
    return QtGui.QIcon(pmDatabaseDelete())


def pmDatabaseMaintenance():
    return PM(809932, 811428)


def DatabaseMaintenance():
    return QtGui.QIcon(pmDatabaseMaintenance())


def pmAtacante():
    return PM(811428, 812033)


def Atacante():
    return QtGui.QIcon(pmAtacante())


def pmAtacada():
    return PM(812033, 812599)


def Atacada():
    return QtGui.QIcon(pmAtacada())


def pmGoToNext():
    return PM(812599, 813011)


def GoToNext():
    return QtGui.QIcon(pmGoToNext())


def pmBlancas():
    return PM(813011, 813362)


def Blancas():
    return QtGui.QIcon(pmBlancas())


def pmNegras():
    return PM(813362, 813608)


def Negras():
    return QtGui.QIcon(pmNegras())


def pmFolderChange():
    return PM(64756, 67514)


def FolderChange():
    return QtGui.QIcon(pmFolderChange())


def pmMarkers():
    return PM(813608, 815303)


def Markers():
    return QtGui.QIcon(pmMarkers())


def pmTop():
    return PM(815303, 815887)


def Top():
    return QtGui.QIcon(pmTop())


def pmBottom():
    return PM(815887, 816476)


def Bottom():
    return QtGui.QIcon(pmBottom())


def pmSTS():
    return PM(816476, 818667)


def STS():
    return QtGui.QIcon(pmSTS())


def pmRun():
    return PM(818667, 820391)


def Run():
    return QtGui.QIcon(pmRun())


def pmRun2():
    return PM(820391, 821911)


def Run2():
    return QtGui.QIcon(pmRun2())


def pmWorldMap():
    return PM(821911, 824652)


def WorldMap():
    return QtGui.QIcon(pmWorldMap())


def pmAfrica():
    return PM(824652, 827138)


def Africa():
    return QtGui.QIcon(pmAfrica())


def pmMaps():
    return PM(827138, 828082)


def Maps():
    return QtGui.QIcon(pmMaps())


def pmSol():
    return PM(828082, 829008)


def Sol():
    return QtGui.QIcon(pmSol())


def pmSolNubes():
    return PM(829008, 829871)


def SolNubes():
    return QtGui.QIcon(pmSolNubes())


def pmSolNubesLluvia():
    return PM(829871, 830831)


def SolNubesLluvia():
    return QtGui.QIcon(pmSolNubesLluvia())


def pmLluvia():
    return PM(830831, 831670)


def Lluvia():
    return QtGui.QIcon(pmLluvia())


def pmInvierno():
    return PM(831670, 833246)


def Invierno():
    return QtGui.QIcon(pmInvierno())


def pmFixedElo():
    return PM(158073, 159336)


def FixedElo():
    return QtGui.QIcon(pmFixedElo())


def pmSoundTool():
    return PM(833246, 835705)


def SoundTool():
    return QtGui.QIcon(pmSoundTool())


def pmTrain():
    return PM(835705, 837075)


def Train():
    return QtGui.QIcon(pmTrain())


def pmPlay():
    return PM(224278, 226367)


def Play():
    return QtGui.QIcon(pmPlay())


def pmMeasure():
    return PM(119858, 121481)


def Measure():
    return QtGui.QIcon(pmMeasure())


def pmPlayGame():
    return PM(837075, 841433)


def PlayGame():
    return QtGui.QIcon(pmPlayGame())


def pmScanner():
    return PM(841433, 841774)


def Scanner():
    return QtGui.QIcon(pmScanner())


def pmCursorScanner():
    return PM(841774, 842091)


def CursorScanner():
    return QtGui.QIcon(pmCursorScanner())


def pmMenos():
    return PM(842091, 842616)


def Menos():
    return QtGui.QIcon(pmMenos())


def pmSchool():
    return PM(842616, 843978)


def School():
    return QtGui.QIcon(pmSchool())


def pmLaw():
    return PM(843978, 844594)


def Law():
    return QtGui.QIcon(pmLaw())


def pmLearnGame():
    return PM(844594, 845027)


def LearnGame():
    return QtGui.QIcon(pmLearnGame())


def pmLonghaul():
    return PM(845027, 845953)


def Longhaul():
    return QtGui.QIcon(pmLonghaul())


def pmTrekking():
    return PM(845953, 846647)


def Trekking():
    return QtGui.QIcon(pmTrekking())


def pmPassword():
    return PM(846647, 847100)


def Password():
    return QtGui.QIcon(pmPassword())


def pmSQL_RAW():
    return PM(837075, 841433)


def SQL_RAW():
    return QtGui.QIcon(pmSQL_RAW())


def pmSun():
    return PM(303502, 304380)


def Sun():
    return QtGui.QIcon(pmSun())


def pmLight32():
    return PM(847100, 848800)


def Light32():
    return QtGui.QIcon(pmLight32())


def pmTOL():
    return PM(848800, 849509)


def TOL():
    return QtGui.QIcon(pmTOL())


def pmUned():
    return PM(849509, 849929)


def Uned():
    return QtGui.QIcon(pmUned())


def pmUwe():
    return PM(849929, 850898)


def Uwe():
    return QtGui.QIcon(pmUwe())


def pmThinking():
    return PM(850898, 851687)


def Thinking():
    return QtGui.QIcon(pmThinking())


def pmWashingMachine():
    return PM(851687, 852350)


def WashingMachine():
    return QtGui.QIcon(pmWashingMachine())


def pmTerminal():
    return PM(852350, 855894)


def Terminal():
    return QtGui.QIcon(pmTerminal())


def pmManualSave():
    return PM(855894, 856477)


def ManualSave():
    return QtGui.QIcon(pmManualSave())


def pmSettings():
    return PM(856477, 856915)


def Settings():
    return QtGui.QIcon(pmSettings())


def pmStrength():
    return PM(856915, 857586)


def Strength():
    return QtGui.QIcon(pmStrength())


def pmSingular():
    return PM(857586, 858441)


def Singular():
    return QtGui.QIcon(pmSingular())


def pmScript():
    return PM(858441, 859010)


def Script():
    return QtGui.QIcon(pmScript())


def pmTexto():
    return PM(859010, 861855)


def Texto():
    return QtGui.QIcon(pmTexto())


def pmLampara():
    return PM(861855, 862564)


def Lampara():
    return QtGui.QIcon(pmLampara())


def pmFile():
    return PM(862564, 864864)


def File():
    return QtGui.QIcon(pmFile())


def pmCalculo():
    return PM(864864, 865790)


def Calculo():
    return QtGui.QIcon(pmCalculo())


def pmOpeningLines():
    return PM(865790, 866468)


def OpeningLines():
    return QtGui.QIcon(pmOpeningLines())


def pmStudy():
    return PM(866468, 867381)


def Study():
    return QtGui.QIcon(pmStudy())


def pmLichess():
    return PM(867381, 868269)


def Lichess():
    return QtGui.QIcon(pmLichess())


def pmMiniatura():
    return PM(868269, 869196)


def Miniatura():
    return QtGui.QIcon(pmMiniatura())


def pmLocomotora():
    return PM(869196, 869977)


def Locomotora():
    return QtGui.QIcon(pmLocomotora())


def pmTrainSequential():
    return PM(869977, 871118)


def TrainSequential():
    return QtGui.QIcon(pmTrainSequential())


def pmTrainStatic():
    return PM(871118, 872078)


def TrainStatic():
    return QtGui.QIcon(pmTrainStatic())


def pmTrainPositions():
    return PM(872078, 873059)


def TrainPositions():
    return QtGui.QIcon(pmTrainPositions())


def pmTrainEngines():
    return PM(873059, 874493)


def TrainEngines():
    return QtGui.QIcon(pmTrainEngines())


def pmError():
    return PM(41940, 45940)


def Error():
    return QtGui.QIcon(pmError())


def pmAtajos():
    return PM(874493, 875672)


def Atajos():
    return QtGui.QIcon(pmAtajos())


def pmTOLline():
    return PM(875672, 876776)


def TOLline():
    return QtGui.QIcon(pmTOLline())


def pmTOLchange():
    return PM(876776, 878998)


def TOLchange():
    return QtGui.QIcon(pmTOLchange())


def pmPack():
    return PM(878998, 880171)


def Pack():
    return QtGui.QIcon(pmPack())


def pmHome():
    return PM(173083, 174265)


def Home():
    return QtGui.QIcon(pmHome())


def pmImport8():
    return PM(880171, 880929)


def Import8():
    return QtGui.QIcon(pmImport8())


def pmExport8():
    return PM(880929, 881554)


def Export8():
    return QtGui.QIcon(pmExport8())


def pmTablas8():
    return PM(881554, 882346)


def Tablas8():
    return QtGui.QIcon(pmTablas8())


def pmBlancas8():
    return PM(882346, 883376)


def Blancas8():
    return QtGui.QIcon(pmBlancas8())


def pmNegras8():
    return PM(883376, 884215)


def Negras8():
    return QtGui.QIcon(pmNegras8())


def pmBook():
    return PM(884215, 884789)


def Book():
    return QtGui.QIcon(pmBook())


def pmWrite():
    return PM(884789, 885994)


def Write():
    return QtGui.QIcon(pmWrite())


def pmAlt():
    return PM(885994, 886436)


def Alt():
    return QtGui.QIcon(pmAlt())


def pmShift():
    return PM(886436, 886776)


def Shift():
    return QtGui.QIcon(pmShift())


def pmRightMouse():
    return PM(886776, 887576)


def RightMouse():
    return QtGui.QIcon(pmRightMouse())


def pmControl():
    return PM(887576, 888101)


def Control():
    return QtGui.QIcon(pmControl())


def pmFinales():
    return PM(888101, 889188)


def Finales():
    return QtGui.QIcon(pmFinales())


def pmEditColumns():
    return PM(889188, 889920)


def EditColumns():
    return QtGui.QIcon(pmEditColumns())


def pmResizeAll():
    return PM(889920, 890430)


def ResizeAll():
    return QtGui.QIcon(pmResizeAll())


def pmChecked():
    return PM(890430, 890936)


def Checked():
    return QtGui.QIcon(pmChecked())


def pmUnchecked():
    return PM(890936, 891184)


def Unchecked():
    return QtGui.QIcon(pmUnchecked())


def pmBuscarC():
    return PM(891184, 891628)


def BuscarC():
    return QtGui.QIcon(pmBuscarC())


def pmPeonBlanco():
    return PM(891628, 893809)


def PeonBlanco():
    return QtGui.QIcon(pmPeonBlanco())


def pmPeonNegro():
    return PM(893809, 895333)


def PeonNegro():
    return QtGui.QIcon(pmPeonNegro())


def pmReciclar():
    return PM(895333, 896057)


def Reciclar():
    return QtGui.QIcon(pmReciclar())


def pmLanzamiento():
    return PM(896057, 896770)


def Lanzamiento():
    return QtGui.QIcon(pmLanzamiento())


def pmEndGame():
    return PM(896770, 897184)


def EndGame():
    return QtGui.QIcon(pmEndGame())


def pmPause():
    return PM(897184, 898053)


def Pause():
    return QtGui.QIcon(pmPause())


def pmContinue():
    return PM(898053, 899257)


def Continue():
    return QtGui.QIcon(pmContinue())


def pmClose():
    return PM(899257, 899956)


def Close():
    return QtGui.QIcon(pmClose())


def pmStop():
    return PM(899956, 900989)


def Stop():
    return QtGui.QIcon(pmStop())


def pmFactoryPolyglot():
    return PM(900989, 901809)


def FactoryPolyglot():
    return QtGui.QIcon(pmFactoryPolyglot())


def pmTags():
    return PM(901809, 902632)


def Tags():
    return QtGui.QIcon(pmTags())


def pmAppearance():
    return PM(902632, 903359)


def Appearance():
    return QtGui.QIcon(pmAppearance())


def pmFill():
    return PM(903359, 904397)


def Fill():
    return QtGui.QIcon(pmFill())


def pmSupport():
    return PM(904397, 905129)


def Support():
    return QtGui.QIcon(pmSupport())


def pmOrder():
    return PM(905129, 905927)


def Order():
    return QtGui.QIcon(pmOrder())


def pmPlay1():
    return PM(905927, 907222)


def Play1():
    return QtGui.QIcon(pmPlay1())


def pmRemove1():
    return PM(907222, 908349)


def Remove1():
    return QtGui.QIcon(pmRemove1())


def pmNew1():
    return PM(908349, 908671)


def New1():
    return QtGui.QIcon(pmNew1())


def pmMensError():
    return PM(908671, 910735)


def MensError():
    return QtGui.QIcon(pmMensError())


def pmMensInfo():
    return PM(910735, 913290)


def MensInfo():
    return QtGui.QIcon(pmMensInfo())


def pmJump():
    return PM(913290, 913965)


def Jump():
    return QtGui.QIcon(pmJump())


def pmCaptures():
    return PM(913965, 915146)


def Captures():
    return QtGui.QIcon(pmCaptures())


def pmRepeat():
    return PM(915146, 915805)


def Repeat():
    return QtGui.QIcon(pmRepeat())


def pmCount():
    return PM(915805, 916481)


def Count():
    return QtGui.QIcon(pmCount())


def pmMate15():
    return PM(916481, 917552)


def Mate15():
    return QtGui.QIcon(pmMate15())


def pmCoordinates():
    return PM(917552, 918705)


def Coordinates():
    return QtGui.QIcon(pmCoordinates())


def pmKnight():
    return PM(918705, 919948)


def Knight():
    return QtGui.QIcon(pmKnight())


def pmCorrecto():
    return PM(919948, 920974)


def Correcto():
    return QtGui.QIcon(pmCorrecto())


def pmBlocks():
    return PM(920974, 921311)


def Blocks():
    return QtGui.QIcon(pmBlocks())


def pmWest():
    return PM(921311, 922417)


def West():
    return QtGui.QIcon(pmWest())


def pmOpening():
    return PM(922417, 922675)


def Opening():
    return QtGui.QIcon(pmOpening())


def pmVariation():
    return PM(215618, 216036)


def Variation():
    return QtGui.QIcon(pmVariation())


def pmComment():
    return PM(922675, 923038)


def Comment():
    return QtGui.QIcon(pmComment())


def pmVariationComment():
    return PM(923038, 923382)


def VariationComment():
    return QtGui.QIcon(pmVariationComment())


def pmOpeningVariation():
    return PM(923382, 923846)


def OpeningVariation():
    return QtGui.QIcon(pmOpeningVariation())


def pmOpeningComment():
    return PM(923846, 924179)


def OpeningComment():
    return QtGui.QIcon(pmOpeningComment())


def pmOpeningVariationComment():
    return PM(923382, 923846)


def OpeningVariationComment():
    return QtGui.QIcon(pmOpeningVariationComment())


def pmDeleteRow():
    return PM(924179, 924610)


def DeleteRow():
    return QtGui.QIcon(pmDeleteRow())


def pmDeleteColumn():
    return PM(924610, 925053)


def DeleteColumn():
    return QtGui.QIcon(pmDeleteColumn())


def pmEditVariation():
    return PM(925053, 925408)


def EditVariation():
    return QtGui.QIcon(pmEditVariation())


def pmKibitzer():
    return PM(925408, 926007)


def Kibitzer():
    return QtGui.QIcon(pmKibitzer())


def pmKibitzer_Pause():
    return PM(926007, 926179)


def Kibitzer_Pause():
    return QtGui.QIcon(pmKibitzer_Pause())


def pmKibitzer_Options():
    return PM(926179, 927081)


def Kibitzer_Options():
    return QtGui.QIcon(pmKibitzer_Options())


def pmKibitzer_Voyager():
    return PM(338347, 339190)


def Kibitzer_Voyager():
    return QtGui.QIcon(pmKibitzer_Voyager())


def pmKibitzer_Close():
    return PM(927081, 927638)


def Kibitzer_Close():
    return QtGui.QIcon(pmKibitzer_Close())


def pmKibitzer_Down():
    return PM(927638, 928027)


def Kibitzer_Down():
    return QtGui.QIcon(pmKibitzer_Down())


def pmKibitzer_Up():
    return PM(928027, 928422)


def Kibitzer_Up():
    return QtGui.QIcon(pmKibitzer_Up())


def pmKibitzer_Back():
    return PM(928422, 928855)


def Kibitzer_Back():
    return QtGui.QIcon(pmKibitzer_Back())


def pmKibitzer_Clipboard():
    return PM(928855, 929241)


def Kibitzer_Clipboard():
    return QtGui.QIcon(pmKibitzer_Clipboard())


def pmKibitzer_Play():
    return PM(929241, 929762)


def Kibitzer_Play():
    return QtGui.QIcon(pmKibitzer_Play())


def pmKibitzer_Side():
    return PM(929762, 930515)


def Kibitzer_Side():
    return QtGui.QIcon(pmKibitzer_Side())


def pmKibitzer_Board():
    return PM(930515, 930953)


def Kibitzer_Board():
    return QtGui.QIcon(pmKibitzer_Board())


def pmBoard():
    return PM(930953, 931422)


def Board():
    return QtGui.QIcon(pmBoard())


def pmTraining_Games():
    return PM(931422, 933114)


def Training_Games():
    return QtGui.QIcon(pmTraining_Games())


def pmTraining_Basic():
    return PM(933114, 934487)


def Training_Basic():
    return QtGui.QIcon(pmTraining_Basic())


def pmTraining_Tactics():
    return PM(934487, 935268)


def Training_Tactics():
    return QtGui.QIcon(pmTraining_Tactics())


def pmTraining_Endings():
    return PM(935268, 936202)


def Training_Endings():
    return QtGui.QIcon(pmTraining_Endings())


def pmBridge():
    return PM(936202, 937220)


def Bridge():
    return QtGui.QIcon(pmBridge())


def pmMaia():
    return PM(937220, 938004)


def Maia():
    return QtGui.QIcon(pmMaia())


def pmBinBook():
    return PM(938004, 938753)


def BinBook():
    return QtGui.QIcon(pmBinBook())


def pmConnected():
    return PM(938753, 940371)


def Connected():
    return QtGui.QIcon(pmConnected())


def pmThemes():
    return PM(940371, 940940)


def Themes():
    return QtGui.QIcon(pmThemes())


def pmReset():
    return PM(940940, 942559)


def Reset():
    return QtGui.QIcon(pmReset())


def pmInstall():
    return PM(942559, 944688)


def Install():
    return QtGui.QIcon(pmInstall())


def pmUninstall():
    return PM(944688, 946714)


def Uninstall():
    return QtGui.QIcon(pmUninstall())


def pmLive():
    return PM(946714, 950197)


def Live():
    return QtGui.QIcon(pmLive())


def pmLauncher():
    return PM(950197, 954872)


def Launcher():
    return QtGui.QIcon(pmLauncher())


def pmLogInactive():
    return PM(954872, 955403)


def LogInactive():
    return QtGui.QIcon(pmLogInactive())


def pmLogActive():
    return PM(955403, 955967)


def LogActive():
    return QtGui.QIcon(pmLogActive())


def pmFolderAnil():
    return PM(955967, 956331)


def FolderAnil():
    return QtGui.QIcon(pmFolderAnil())


def pmFolderBlack():
    return PM(956331, 956668)


def FolderBlack():
    return QtGui.QIcon(pmFolderBlack())


def pmFolderBlue():
    return PM(956668, 957042)


def FolderBlue():
    return QtGui.QIcon(pmFolderBlue())


def pmFolderGreen():
    return PM(957042, 957414)


def FolderGreen():
    return QtGui.QIcon(pmFolderGreen())


def pmFolderMagenta():
    return PM(957414, 957787)


def FolderMagenta():
    return QtGui.QIcon(pmFolderMagenta())


def pmFolderRed():
    return PM(957787, 958151)


def FolderRed():
    return QtGui.QIcon(pmFolderRed())


def pmThis():
    return PM(958151, 958605)


def This():
    return QtGui.QIcon(pmThis())


def pmAll():
    return PM(958605, 959108)


def All():
    return QtGui.QIcon(pmAll())


def pmPrevious():
    return PM(959108, 959567)


def Previous():
    return QtGui.QIcon(pmPrevious())


def pmLine():
    return PM(959567, 959754)


def Line():
    return QtGui.QIcon(pmLine())


def pmEmpty():
    return PM(959754, 959839)


def Empty():
    return QtGui.QIcon(pmEmpty())


def pmMore():
    return PM(959839, 960128)


def More():
    return QtGui.QIcon(pmMore())


def pmSelectLogo():
    return PM(960128, 960734)


def SelectLogo():
    return QtGui.QIcon(pmSelectLogo())


def pmSelect():
    return PM(960734, 961388)


def Select():
    return QtGui.QIcon(pmSelect())


def pmSelectClose():
    return PM(961388, 962160)


def SelectClose():
    return QtGui.QIcon(pmSelectClose())


def pmSelectHome():
    return PM(962160, 962942)


def SelectHome():
    return QtGui.QIcon(pmSelectHome())


def pmSelectHistory():
    return PM(962942, 963494)


def SelectHistory():
    return QtGui.QIcon(pmSelectHistory())


def pmSelectExplorer():
    return PM(963494, 964227)


def SelectExplorer():
    return QtGui.QIcon(pmSelectExplorer())


def pmSelectFolderCreate():
    return PM(964227, 965146)


def SelectFolderCreate():
    return QtGui.QIcon(pmSelectFolderCreate())


def pmSelectFolderRemove():
    return PM(965146, 966173)


def SelectFolderRemove():
    return QtGui.QIcon(pmSelectFolderRemove())


def pmSelectReload():
    return PM(966173, 967827)


def SelectReload():
    return QtGui.QIcon(pmSelectReload())


def pmSelectAccept():
    return PM(967827, 968628)


def SelectAccept():
    return QtGui.QIcon(pmSelectAccept())


def pmWiki():
    return PM(968628, 969745)


def Wiki():
    return QtGui.QIcon(pmWiki())


def pmCircle():
    return PM(969745, 971205)


def Circle():
    return QtGui.QIcon(pmCircle())


def pmSortAZ():
    return PM(971205, 971969)


def SortAZ():
    return QtGui.QIcon(pmSortAZ())


def pmReference():
    return PM(971969, 973080)


def Reference():
    return QtGui.QIcon(pmReference())


def pmLanguageNew():
    return PM(973080, 973807)


def LanguageNew():
    return QtGui.QIcon(pmLanguageNew())


def pmODT():
    return PM(973807, 974922)


def ODT():
    return QtGui.QIcon(pmODT())


def pmEngines():
    return PM(974922, 976408)


def Engines():
    return QtGui.QIcon(pmEngines())


def pmConfEngines():
    return PM(976408, 977604)


def ConfEngines():
    return QtGui.QIcon(pmConfEngines())


def pmEngine():
    return PM(977604, 979028)


def Engine():
    return QtGui.QIcon(pmEngine())


def pmZip():
    return PM(979028, 979924)


def Zip():
    return QtGui.QIcon(pmZip())


def pmUpdate():
    return PM(979924, 981008)


def Update():
    return QtGui.QIcon(pmUpdate())


def pmDGT():
    return PM(981008, 982002)


def DGT():
    return QtGui.QIcon(pmDGT())


def pmDGTB():
    return PM(982002, 982704)


def DGTB():
    return QtGui.QIcon(pmDGTB())


def pmMillenium():
    return PM(982704, 983941)


def Millenium():
    return QtGui.QIcon(pmMillenium())


def pmCertabo():
    return PM(983941, 984726)


def Certabo():
    return QtGui.QIcon(pmCertabo())


def pmNovag():
    return PM(984726, 985593)


def Novag():
    return QtGui.QIcon(pmNovag())


def pmChessnut():
    return PM(985593, 986368)


def Chessnut():
    return QtGui.QIcon(pmChessnut())


def pmSquareOff():
    return PM(986368, 987124)


def SquareOff():
    return QtGui.QIcon(pmSquareOff())


def pmRodent():
    return PM(987124, 988242)


def Rodent():
    return QtGui.QIcon(pmRodent())


def pmLeague():
    return PM(988242, 989572)


def League():
    return QtGui.QIcon(pmLeague())


def pmJourney():
    return PM(989572, 990811)


def Journey():
    return QtGui.QIcon(pmJourney())


def pmClassification():
    return PM(990811, 991330)


def Classification():
    return QtGui.QIcon(pmClassification())
