from PySide2 import QtGui

import Code

f = open(Code.path_resource("IntFiles", "Iconos.bin"), "rb")
binIconos = f.read()
f.close()


def icono(name):
    return eval("%s()"%name)


def pixmap(name):
    return eval("pm%s()"%name)


def PM(desde, hasta):
    pm = QtGui.QPixmap()
    pm.loadFromData(binIconos[desde:hasta])
    return pm

def pmLM():
    return PM(0,1248)


def LM():
    return QtGui.QIcon(pmLM())


def pmAplicacion64():
    return PM(1248,6430)


def Aplicacion64():
    return QtGui.QIcon(pmAplicacion64())


def pmDatos():
    return PM(6430,7617)


def Datos():
    return QtGui.QIcon(pmDatos())


def pmTutor():
    return PM(7617,9646)


def Tutor():
    return QtGui.QIcon(pmTutor())


def pmPartidaOriginal():
    return PM(9646,11623)


def PartidaOriginal():
    return QtGui.QIcon(pmPartidaOriginal())


def pmDGT():
    return PM(11623,12617)


def DGT():
    return QtGui.QIcon(pmDGT())


def pmDGTB():
    return PM(12617,14041)


def DGTB():
    return QtGui.QIcon(pmDGTB())


def pmMillenium():
    return PM(14041,15278)


def Millenium():
    return QtGui.QIcon(pmMillenium())


def pmCertabo():
    return PM(15278,16063)


def Certabo():
    return QtGui.QIcon(pmCertabo())


def pmNovag():
    return PM(16063,16807)


def Novag():
    return QtGui.QIcon(pmNovag())


def pmFindAllMoves():
    return PM(16807,18403)


def FindAllMoves():
    return QtGui.QIcon(pmFindAllMoves())


def pmResizeBoard():
    return PM(16807,18403)


def ResizeBoard():
    return QtGui.QIcon(pmResizeBoard())


def pmMensEspera():
    return PM(18403,22151)


def MensEspera():
    return QtGui.QIcon(pmMensEspera())


def pmUtilidades():
    return PM(22151,28580)


def Utilidades():
    return QtGui.QIcon(pmUtilidades())


def pmTerminar():
    return PM(28580,30330)


def Terminar():
    return QtGui.QIcon(pmTerminar())


def pmNuevaPartida():
    return PM(30330,32078)


def NuevaPartida():
    return QtGui.QIcon(pmNuevaPartida())


def pmOpciones():
    return PM(32078,33806)


def Opciones():
    return QtGui.QIcon(pmOpciones())


def pmEntrenamiento():
    return PM(7617,9646)


def Entrenamiento():
    return QtGui.QIcon(pmEntrenamiento())


def pmAplazar():
    return PM(33806,36873)


def Aplazar():
    return QtGui.QIcon(pmAplazar())


def pmAplazamientos():
    return PM(36873,40189)


def Aplazamientos():
    return QtGui.QIcon(pmAplazamientos())


def pmCapturas():
    return PM(40189,42230)


def Capturas():
    return QtGui.QIcon(pmCapturas())


def pmReiniciar():
    return PM(42230,44524)


def Reiniciar():
    return QtGui.QIcon(pmReiniciar())


def pmImportarGM():
    return PM(44524,47124)


def ImportarGM():
    return QtGui.QIcon(pmImportarGM())


def pmAbandonar():
    return PM(47124,51124)


def Abandonar():
    return QtGui.QIcon(pmAbandonar())


def pmEmpezar():
    return PM(51124,53160)


def Empezar():
    return QtGui.QIcon(pmEmpezar())


def pmOtros():
    return PM(53160,57630)


def Otros():
    return QtGui.QIcon(pmOtros())


def pmAnalizar():
    return PM(57630,59167)


def Analizar():
    return QtGui.QIcon(pmAnalizar())


def pmMainMenu():
    return PM(59167,63477)


def MainMenu():
    return QtGui.QIcon(pmMainMenu())


def pmFinPartida():
    return PM(63477,66425)


def FinPartida():
    return QtGui.QIcon(pmFinPartida())


def pmGrabar():
    return PM(66425,67888)


def Grabar():
    return QtGui.QIcon(pmGrabar())


def pmGrabarComo():
    return PM(67888,69940)


def GrabarComo():
    return QtGui.QIcon(pmGrabarComo())


def pmRecuperar():
    return PM(69940,72698)


def Recuperar():
    return QtGui.QIcon(pmRecuperar())


def pmInformacion():
    return PM(72698,74657)


def Informacion():
    return QtGui.QIcon(pmInformacion())


def pmNuevo():
    return PM(74657,75411)


def Nuevo():
    return QtGui.QIcon(pmNuevo())


def pmCopiar():
    return PM(75411,76592)


def Copiar():
    return QtGui.QIcon(pmCopiar())


def pmModificar():
    return PM(76592,80989)


def Modificar():
    return QtGui.QIcon(pmModificar())


def pmBorrar():
    return PM(80989,85980)


def Borrar():
    return QtGui.QIcon(pmBorrar())


def pmMarcar():
    return PM(85980,90909)


def Marcar():
    return QtGui.QIcon(pmMarcar())


def pmPegar():
    return PM(90909,93220)


def Pegar():
    return QtGui.QIcon(pmPegar())


def pmFichero():
    return PM(93220,97905)


def Fichero():
    return QtGui.QIcon(pmFichero())


def pmNuestroFichero():
    return PM(97905,100952)


def NuestroFichero():
    return QtGui.QIcon(pmNuestroFichero())


def pmFicheroRepite():
    return PM(100952,102448)


def FicheroRepite():
    return QtGui.QIcon(pmFicheroRepite())


def pmInformacionPGN():
    return PM(102448,103466)


def InformacionPGN():
    return QtGui.QIcon(pmInformacionPGN())


def pmVer():
    return PM(103466,104920)


def Ver():
    return QtGui.QIcon(pmVer())


def pmInicio():
    return PM(104920,106934)


def Inicio():
    return QtGui.QIcon(pmInicio())


def pmFinal():
    return PM(106934,108928)


def Final():
    return QtGui.QIcon(pmFinal())


def pmFiltrar():
    return PM(108928,115418)


def Filtrar():
    return QtGui.QIcon(pmFiltrar())


def pmArriba():
    return PM(115418,117571)


def Arriba():
    return QtGui.QIcon(pmArriba())


def pmAbajo():
    return PM(117571,119679)


def Abajo():
    return QtGui.QIcon(pmAbajo())


def pmEstadisticas():
    return PM(119679,121818)


def Estadisticas():
    return QtGui.QIcon(pmEstadisticas())


def pmCheck():
    return PM(121818,125042)


def Check():
    return QtGui.QIcon(pmCheck())


def pmTablas():
    return PM(125042,126665)


def Tablas():
    return QtGui.QIcon(pmTablas())


def pmAtras():
    return PM(126665,128184)


def Atras():
    return QtGui.QIcon(pmAtras())


def pmBuscar():
    return PM(128184,130169)


def Buscar():
    return QtGui.QIcon(pmBuscar())


def pmLibros():
    return PM(130169,132297)


def Libros():
    return QtGui.QIcon(pmLibros())


def pmAceptar():
    return PM(132297,135644)


def Aceptar():
    return QtGui.QIcon(pmAceptar())


def pmCancelar():
    return PM(135644,137627)


def Cancelar():
    return QtGui.QIcon(pmCancelar())


def pmDefecto():
    return PM(137627,140946)


def Defecto():
    return QtGui.QIcon(pmDefecto())


def pmInsertar():
    return PM(140946,143342)


def Insertar():
    return QtGui.QIcon(pmInsertar())


def pmJugar():
    return PM(143342,145551)


def Jugar():
    return QtGui.QIcon(pmJugar())


def pmConfigurar():
    return PM(145551,148635)


def Configurar():
    return QtGui.QIcon(pmConfigurar())


def pmS_Aceptar():
    return PM(132297,135644)


def S_Aceptar():
    return QtGui.QIcon(pmS_Aceptar())


def pmS_Cancelar():
    return PM(135644,137627)


def S_Cancelar():
    return QtGui.QIcon(pmS_Cancelar())


def pmS_Microfono():
    return PM(148635,154076)


def S_Microfono():
    return QtGui.QIcon(pmS_Microfono())


def pmS_LeerWav():
    return PM(44524,47124)


def S_LeerWav():
    return QtGui.QIcon(pmS_LeerWav())


def pmS_Play():
    return PM(154076,159414)


def S_Play():
    return QtGui.QIcon(pmS_Play())


def pmS_StopPlay():
    return PM(159414,160024)


def S_StopPlay():
    return QtGui.QIcon(pmS_StopPlay())


def pmS_StopMicrofono():
    return PM(159414,160024)


def S_StopMicrofono():
    return QtGui.QIcon(pmS_StopMicrofono())


def pmS_Record():
    return PM(160024,163257)


def S_Record():
    return QtGui.QIcon(pmS_Record())


def pmS_Limpiar():
    return PM(80989,85980)


def S_Limpiar():
    return QtGui.QIcon(pmS_Limpiar())


def pmHistorial():
    return PM(163257,164520)


def Historial():
    return QtGui.QIcon(pmHistorial())


def pmPegar16():
    return PM(164520,165514)


def Pegar16():
    return QtGui.QIcon(pmPegar16())


def pmRivalesMP():
    return PM(165514,168196)


def RivalesMP():
    return QtGui.QIcon(pmRivalesMP())


def pmCamara():
    return PM(168196,169718)


def Camara():
    return QtGui.QIcon(pmCamara())


def pmUsuarios():
    return PM(169718,170958)


def Usuarios():
    return QtGui.QIcon(pmUsuarios())


def pmResistencia():
    return PM(170958,174020)


def Resistencia():
    return QtGui.QIcon(pmResistencia())


def pmCebra():
    return PM(174020,176473)


def Cebra():
    return QtGui.QIcon(pmCebra())


def pmGafas():
    return PM(176473,177631)


def Gafas():
    return QtGui.QIcon(pmGafas())


def pmPuente():
    return PM(177631,178267)


def Puente():
    return QtGui.QIcon(pmPuente())


def pmWeb():
    return PM(178267,179449)


def Web():
    return QtGui.QIcon(pmWeb())


def pmMail():
    return PM(179449,180409)


def Mail():
    return QtGui.QIcon(pmMail())


def pmAyuda():
    return PM(180409,181590)


def Ayuda():
    return QtGui.QIcon(pmAyuda())


def pmFAQ():
    return PM(181590,182911)


def FAQ():
    return QtGui.QIcon(pmFAQ())


def pmActualiza():
    return PM(182911,183777)


def Actualiza():
    return QtGui.QIcon(pmActualiza())


def pmRefresh():
    return PM(183777,186169)


def Refresh():
    return QtGui.QIcon(pmRefresh())


def pmJuegaSolo():
    return PM(186169,188021)


def JuegaSolo():
    return QtGui.QIcon(pmJuegaSolo())


def pmPlayer():
    return PM(188021,189203)


def Player():
    return QtGui.QIcon(pmPlayer())


def pmJS_Rotacion():
    return PM(189203,191113)


def JS_Rotacion():
    return QtGui.QIcon(pmJS_Rotacion())


def pmElo():
    return PM(191113,192619)


def Elo():
    return QtGui.QIcon(pmElo())


def pmMate():
    return PM(192619,193180)


def Mate():
    return QtGui.QIcon(pmMate())


def pmEloTimed():
    return PM(193180,194664)


def EloTimed():
    return QtGui.QIcon(pmEloTimed())


def pmPGN():
    return PM(194664,196662)


def PGN():
    return QtGui.QIcon(pmPGN())


def pmPGN_Importar():
    return PM(196662,198252)


def PGN_Importar():
    return QtGui.QIcon(pmPGN_Importar())


def pmAyudaGR():
    return PM(198252,204130)


def AyudaGR():
    return QtGui.QIcon(pmAyudaGR())


def pmBotonAyuda():
    return PM(204130,206590)


def BotonAyuda():
    return QtGui.QIcon(pmBotonAyuda())


def pmColores():
    return PM(206590,207821)


def Colores():
    return QtGui.QIcon(pmColores())


def pmEditarColores():
    return PM(207821,210124)


def EditarColores():
    return QtGui.QIcon(pmEditarColores())


def pmGranMaestro():
    return PM(210124,210980)


def GranMaestro():
    return QtGui.QIcon(pmGranMaestro())


def pmFavoritos():
    return PM(210980,212746)


def Favoritos():
    return QtGui.QIcon(pmFavoritos())


def pmCarpeta():
    return PM(212746,213450)


def Carpeta():
    return QtGui.QIcon(pmCarpeta())


def pmDivision():
    return PM(213450,214115)


def Division():
    return QtGui.QIcon(pmDivision())


def pmDivisionF():
    return PM(214115,215229)


def DivisionF():
    return QtGui.QIcon(pmDivisionF())


def pmDelete():
    return PM(215229,216153)


def Delete():
    return QtGui.QIcon(pmDelete())


def pmModificarP():
    return PM(216153,217219)


def ModificarP():
    return QtGui.QIcon(pmModificarP())


def pmGrupo_Si():
    return PM(217219,217681)


def Grupo_Si():
    return QtGui.QIcon(pmGrupo_Si())


def pmGrupo_No():
    return PM(217681,218004)


def Grupo_No():
    return QtGui.QIcon(pmGrupo_No())


def pmMotor_Si():
    return PM(218004,218466)


def Motor_Si():
    return QtGui.QIcon(pmMotor_Si())


def pmMotor_No():
    return PM(215229,216153)


def Motor_No():
    return QtGui.QIcon(pmMotor_No())


def pmMotor_Actual():
    return PM(218466,219483)


def Motor_Actual():
    return QtGui.QIcon(pmMotor_Actual())


def pmMoverInicio():
    return PM(219483,219781)


def MoverInicio():
    return QtGui.QIcon(pmMoverInicio())


def pmMoverFinal():
    return PM(219781,220082)


def MoverFinal():
    return QtGui.QIcon(pmMoverFinal())


def pmMoverAdelante():
    return PM(220082,220437)


def MoverAdelante():
    return QtGui.QIcon(pmMoverAdelante())


def pmMoverAtras():
    return PM(220437,220802)


def MoverAtras():
    return QtGui.QIcon(pmMoverAtras())


def pmMoverLibre():
    return PM(220802,221220)


def MoverLibre():
    return QtGui.QIcon(pmMoverLibre())


def pmMoverTiempo():
    return PM(221220,221799)


def MoverTiempo():
    return QtGui.QIcon(pmMoverTiempo())


def pmMoverMas():
    return PM(221799,222838)


def MoverMas():
    return QtGui.QIcon(pmMoverMas())


def pmMoverGrabar():
    return PM(222838,223694)


def MoverGrabar():
    return QtGui.QIcon(pmMoverGrabar())


def pmMoverGrabarTodos():
    return PM(223694,224738)


def MoverGrabarTodos():
    return QtGui.QIcon(pmMoverGrabarTodos())


def pmMoverJugar():
    return PM(224738,225569)


def MoverJugar():
    return QtGui.QIcon(pmMoverJugar())


def pmPelicula():
    return PM(225569,227703)


def Pelicula():
    return QtGui.QIcon(pmPelicula())


def pmPelicula_Pausa():
    return PM(227703,229462)


def Pelicula_Pausa():
    return QtGui.QIcon(pmPelicula_Pausa())


def pmPelicula_Seguir():
    return PM(229462,231551)


def Pelicula_Seguir():
    return QtGui.QIcon(pmPelicula_Seguir())


def pmPelicula_Rapido():
    return PM(231551,233610)


def Pelicula_Rapido():
    return QtGui.QIcon(pmPelicula_Rapido())


def pmPelicula_Lento():
    return PM(233610,235485)


def Pelicula_Lento():
    return QtGui.QIcon(pmPelicula_Lento())


def pmPelicula_Repetir():
    return PM(42230,44524)


def Pelicula_Repetir():
    return QtGui.QIcon(pmPelicula_Repetir())


def pmPelicula_PGN():
    return PM(235485,236393)


def Pelicula_PGN():
    return QtGui.QIcon(pmPelicula_PGN())


def pmMemoria():
    return PM(236393,238334)


def Memoria():
    return QtGui.QIcon(pmMemoria())


def pmEntrenar():
    return PM(238334,239873)


def Entrenar():
    return QtGui.QIcon(pmEntrenar())


def pmEnviar():
    return PM(238334,239873)


def Enviar():
    return QtGui.QIcon(pmEnviar())


def pmBoxRooms():
    return PM(239873,244676)


def BoxRooms():
    return QtGui.QIcon(pmBoxRooms())


def pmBoxRoom():
    return PM(244676,245138)


def BoxRoom():
    return QtGui.QIcon(pmBoxRoom())


def pmNewBoxRoom():
    return PM(245138,246646)


def NewBoxRoom():
    return QtGui.QIcon(pmNewBoxRoom())


def pmNuevoMas():
    return PM(245138,246646)


def NuevoMas():
    return QtGui.QIcon(pmNuevoMas())


def pmTemas():
    return PM(246646,248869)


def Temas():
    return QtGui.QIcon(pmTemas())


def pmTutorialesCrear():
    return PM(248869,255138)


def TutorialesCrear():
    return QtGui.QIcon(pmTutorialesCrear())


def pmMover():
    return PM(255138,255720)


def Mover():
    return QtGui.QIcon(pmMover())


def pmSeleccionar():
    return PM(255720,261424)


def Seleccionar():
    return QtGui.QIcon(pmSeleccionar())


def pmVista():
    return PM(261424,263348)


def Vista():
    return QtGui.QIcon(pmVista())


def pmInformacionPGNUno():
    return PM(263348,264726)


def InformacionPGNUno():
    return QtGui.QIcon(pmInformacionPGNUno())


def pmDailyTest():
    return PM(264726,267066)


def DailyTest():
    return QtGui.QIcon(pmDailyTest())


def pmJuegaPorMi():
    return PM(267066,268786)


def JuegaPorMi():
    return QtGui.QIcon(pmJuegaPorMi())


def pmArbol():
    return PM(268786,269420)


def Arbol():
    return QtGui.QIcon(pmArbol())


def pmGrabarFichero():
    return PM(66425,67888)


def GrabarFichero():
    return QtGui.QIcon(pmGrabarFichero())


def pmClipboard():
    return PM(269420,270198)


def Clipboard():
    return QtGui.QIcon(pmClipboard())


def pmFics():
    return PM(270198,270615)


def Fics():
    return QtGui.QIcon(pmFics())


def pmFide():
    return PM(9646,11623)


def Fide():
    return QtGui.QIcon(pmFide())


def pmFichPGN():
    return PM(30330,32078)


def FichPGN():
    return QtGui.QIcon(pmFichPGN())


def pmFlechas():
    return PM(270615,273967)


def Flechas():
    return QtGui.QIcon(pmFlechas())


def pmMarcos():
    return PM(273967,275414)


def Marcos():
    return QtGui.QIcon(pmMarcos())


def pmSVGs():
    return PM(275414,278983)


def SVGs():
    return QtGui.QIcon(pmSVGs())


def pmAmarillo():
    return PM(278983,280235)


def Amarillo():
    return QtGui.QIcon(pmAmarillo())


def pmNaranja():
    return PM(280235,281467)


def Naranja():
    return QtGui.QIcon(pmNaranja())


def pmVerde():
    return PM(281467,282743)


def Verde():
    return QtGui.QIcon(pmVerde())


def pmAzul():
    return PM(282743,283831)


def Azul():
    return QtGui.QIcon(pmAzul())


def pmMagenta():
    return PM(283831,285119)


def Magenta():
    return QtGui.QIcon(pmMagenta())


def pmRojo():
    return PM(285119,286338)


def Rojo():
    return QtGui.QIcon(pmRojo())


def pmGris():
    return PM(286338,287296)


def Gris():
    return QtGui.QIcon(pmGris())


def pmAmarillo32():
    return PM(287296,289276)


def Amarillo32():
    return QtGui.QIcon(pmAmarillo32())


def pmNaranja32():
    return PM(289276,291400)


def Naranja32():
    return QtGui.QIcon(pmNaranja32())


def pmVerde32():
    return PM(291400,293521)


def Verde32():
    return QtGui.QIcon(pmVerde32())


def pmAzul32():
    return PM(293521,295900)


def Azul32():
    return QtGui.QIcon(pmAzul32())


def pmMagenta32():
    return PM(295900,298351)


def Magenta32():
    return QtGui.QIcon(pmMagenta32())


def pmRojo32():
    return PM(298351,300166)


def Rojo32():
    return QtGui.QIcon(pmRojo32())


def pmGris32():
    return PM(300166,302080)


def Gris32():
    return QtGui.QIcon(pmGris32())


def pmPuntoBlanco():
    return PM(302080,302429)


def PuntoBlanco():
    return QtGui.QIcon(pmPuntoBlanco())


def pmPuntoAmarillo():
    return PM(217219,217681)


def PuntoAmarillo():
    return QtGui.QIcon(pmPuntoAmarillo())


def pmPuntoNaranja():
    return PM(302429,302891)


def PuntoNaranja():
    return QtGui.QIcon(pmPuntoNaranja())


def pmPuntoVerde():
    return PM(218004,218466)


def PuntoVerde():
    return QtGui.QIcon(pmPuntoVerde())


def pmPuntoAzul():
    return PM(244676,245138)


def PuntoAzul():
    return QtGui.QIcon(pmPuntoAzul())


def pmPuntoMagenta():
    return PM(302891,303390)


def PuntoMagenta():
    return QtGui.QIcon(pmPuntoMagenta())


def pmPuntoRojo():
    return PM(303390,303889)


def PuntoRojo():
    return QtGui.QIcon(pmPuntoRojo())


def pmPuntoNegro():
    return PM(217681,218004)


def PuntoNegro():
    return QtGui.QIcon(pmPuntoNegro())


def pmPuntoEstrella():
    return PM(303889,304316)


def PuntoEstrella():
    return QtGui.QIcon(pmPuntoEstrella())


def pmComentario():
    return PM(304316,304953)


def Comentario():
    return QtGui.QIcon(pmComentario())


def pmComentarioMas():
    return PM(304953,305892)


def ComentarioMas():
    return QtGui.QIcon(pmComentarioMas())


def pmComentarioEditar():
    return PM(222838,223694)


def ComentarioEditar():
    return QtGui.QIcon(pmComentarioEditar())


def pmOpeningComentario():
    return PM(305892,306888)


def OpeningComentario():
    return QtGui.QIcon(pmOpeningComentario())


def pmMas():
    return PM(306888,307397)


def Mas():
    return QtGui.QIcon(pmMas())


def pmMasR():
    return PM(307397,307885)


def MasR():
    return QtGui.QIcon(pmMasR())


def pmMasDoc():
    return PM(307885,308686)


def MasDoc():
    return QtGui.QIcon(pmMasDoc())


def pmPotencia():
    return PM(182911,183777)


def Potencia():
    return QtGui.QIcon(pmPotencia())


def pmBMT():
    return PM(308686,309564)


def BMT():
    return QtGui.QIcon(pmBMT())


def pmOjo():
    return PM(309564,310686)


def Ojo():
    return QtGui.QIcon(pmOjo())


def pmOcultar():
    return PM(309564,310686)


def Ocultar():
    return QtGui.QIcon(pmOcultar())


def pmMostrar():
    return PM(310686,311742)


def Mostrar():
    return QtGui.QIcon(pmMostrar())


def pmBlog():
    return PM(311742,312264)


def Blog():
    return QtGui.QIcon(pmBlog())


def pmVariations():
    return PM(312264,313171)


def Variations():
    return QtGui.QIcon(pmVariations())


def pmVariationsG():
    return PM(313171,315598)


def VariationsG():
    return QtGui.QIcon(pmVariationsG())


def pmCambiar():
    return PM(315598,317312)


def Cambiar():
    return QtGui.QIcon(pmCambiar())


def pmAnterior():
    return PM(317312,319366)


def Anterior():
    return QtGui.QIcon(pmAnterior())


def pmSiguiente():
    return PM(319366,321436)


def Siguiente():
    return QtGui.QIcon(pmSiguiente())


def pmSiguienteF():
    return PM(321436,323611)


def SiguienteF():
    return QtGui.QIcon(pmSiguienteF())


def pmAnteriorF():
    return PM(323611,325805)


def AnteriorF():
    return QtGui.QIcon(pmAnteriorF())


def pmX():
    return PM(325805,327087)


def X():
    return QtGui.QIcon(pmX())


def pmTools():
    return PM(327087,329688)


def Tools():
    return QtGui.QIcon(pmTools())


def pmTacticas():
    return PM(329688,332261)


def Tacticas():
    return QtGui.QIcon(pmTacticas())


def pmCancelarPeque():
    return PM(332261,332823)


def CancelarPeque():
    return QtGui.QIcon(pmCancelarPeque())


def pmAceptarPeque():
    return PM(218466,219483)


def AceptarPeque():
    return QtGui.QIcon(pmAceptarPeque())


def pmLibre():
    return PM(332823,335215)


def Libre():
    return QtGui.QIcon(pmLibre())


def pmEnBlanco():
    return PM(335215,335941)


def EnBlanco():
    return QtGui.QIcon(pmEnBlanco())


def pmDirector():
    return PM(335941,338915)


def Director():
    return QtGui.QIcon(pmDirector())


def pmTorneos():
    return PM(338915,340653)


def Torneos():
    return QtGui.QIcon(pmTorneos())


def pmOpenings():
    return PM(340653,341578)


def Openings():
    return QtGui.QIcon(pmOpenings())


def pmV_Blancas():
    return PM(341578,341858)


def V_Blancas():
    return QtGui.QIcon(pmV_Blancas())


def pmV_Blancas_Mas():
    return PM(341858,342138)


def V_Blancas_Mas():
    return QtGui.QIcon(pmV_Blancas_Mas())


def pmV_Blancas_Mas_Mas():
    return PM(342138,342410)


def V_Blancas_Mas_Mas():
    return QtGui.QIcon(pmV_Blancas_Mas_Mas())


def pmV_Negras():
    return PM(342410,342685)


def V_Negras():
    return QtGui.QIcon(pmV_Negras())


def pmV_Negras_Mas():
    return PM(342685,342960)


def V_Negras_Mas():
    return QtGui.QIcon(pmV_Negras_Mas())


def pmV_Negras_Mas_Mas():
    return PM(342960,343229)


def V_Negras_Mas_Mas():
    return QtGui.QIcon(pmV_Negras_Mas_Mas())


def pmV_Blancas_Igual_Negras():
    return PM(343229,343531)


def V_Blancas_Igual_Negras():
    return QtGui.QIcon(pmV_Blancas_Igual_Negras())


def pmMezclar():
    return PM(140946,143342)


def Mezclar():
    return QtGui.QIcon(pmMezclar())


def pmVoyager():
    return PM(343531,344374)


def Voyager():
    return QtGui.QIcon(pmVoyager())


def pmVoyager32():
    return PM(344374,346262)


def Voyager32():
    return QtGui.QIcon(pmVoyager32())


def pmReindexar():
    return PM(346262,348079)


def Reindexar():
    return QtGui.QIcon(pmReindexar())


def pmRename():
    return PM(348079,349063)


def Rename():
    return QtGui.QIcon(pmRename())


def pmAdd():
    return PM(349063,350016)


def Add():
    return QtGui.QIcon(pmAdd())


def pmMas22():
    return PM(350016,350680)


def Mas22():
    return QtGui.QIcon(pmMas22())


def pmMenos22():
    return PM(350680,351124)


def Menos22():
    return QtGui.QIcon(pmMenos22())


def pmTransposition():
    return PM(351124,351643)


def Transposition():
    return QtGui.QIcon(pmTransposition())


def pmRat():
    return PM(351643,357347)


def Rat():
    return QtGui.QIcon(pmRat())


def pmAlligator():
    return PM(357347,362339)


def Alligator():
    return QtGui.QIcon(pmAlligator())


def pmAnt():
    return PM(362339,369037)


def Ant():
    return QtGui.QIcon(pmAnt())


def pmBat():
    return PM(369037,371991)


def Bat():
    return QtGui.QIcon(pmBat())


def pmBear():
    return PM(371991,379270)


def Bear():
    return QtGui.QIcon(pmBear())


def pmBee():
    return PM(379270,384272)


def Bee():
    return QtGui.QIcon(pmBee())


def pmBird():
    return PM(384272,390331)


def Bird():
    return QtGui.QIcon(pmBird())


def pmBull():
    return PM(390331,397300)


def Bull():
    return QtGui.QIcon(pmBull())


def pmBulldog():
    return PM(397300,404191)


def Bulldog():
    return QtGui.QIcon(pmBulldog())


def pmButterfly():
    return PM(404191,411565)


def Butterfly():
    return QtGui.QIcon(pmButterfly())


def pmCat():
    return PM(411565,417837)


def Cat():
    return QtGui.QIcon(pmCat())


def pmChicken():
    return PM(417837,423648)


def Chicken():
    return QtGui.QIcon(pmChicken())


def pmCow():
    return PM(423648,430391)


def Cow():
    return QtGui.QIcon(pmCow())


def pmCrab():
    return PM(430391,435980)


def Crab():
    return QtGui.QIcon(pmCrab())


def pmCrocodile():
    return PM(435980,442121)


def Crocodile():
    return QtGui.QIcon(pmCrocodile())


def pmDeer():
    return PM(442121,448428)


def Deer():
    return QtGui.QIcon(pmDeer())


def pmDog():
    return PM(448428,455031)


def Dog():
    return QtGui.QIcon(pmDog())


def pmDonkey():
    return PM(455031,460678)


def Donkey():
    return QtGui.QIcon(pmDonkey())


def pmDuck():
    return PM(460678,467221)


def Duck():
    return QtGui.QIcon(pmDuck())


def pmEagle():
    return PM(467221,472039)


def Eagle():
    return QtGui.QIcon(pmEagle())


def pmElephant():
    return PM(472039,478520)


def Elephant():
    return QtGui.QIcon(pmElephant())


def pmFish():
    return PM(478520,485361)


def Fish():
    return QtGui.QIcon(pmFish())


def pmFox():
    return PM(485361,492144)


def Fox():
    return QtGui.QIcon(pmFox())


def pmFrog():
    return PM(492144,498560)


def Frog():
    return QtGui.QIcon(pmFrog())


def pmGiraffe():
    return PM(498560,505738)


def Giraffe():
    return QtGui.QIcon(pmGiraffe())


def pmGorilla():
    return PM(505738,512277)


def Gorilla():
    return QtGui.QIcon(pmGorilla())


def pmHippo():
    return PM(512277,519398)


def Hippo():
    return QtGui.QIcon(pmHippo())


def pmHorse():
    return PM(519398,525945)


def Horse():
    return QtGui.QIcon(pmHorse())


def pmInsect():
    return PM(525945,531880)


def Insect():
    return QtGui.QIcon(pmInsect())


def pmLion():
    return PM(531880,540790)


def Lion():
    return QtGui.QIcon(pmLion())


def pmMonkey():
    return PM(540790,548469)


def Monkey():
    return QtGui.QIcon(pmMonkey())


def pmMoose():
    return PM(548469,555093)


def Moose():
    return QtGui.QIcon(pmMoose())


def pmMouse():
    return PM(351643,357347)


def Mouse():
    return QtGui.QIcon(pmMouse())


def pmOwl():
    return PM(555093,561799)


def Owl():
    return QtGui.QIcon(pmOwl())


def pmPanda():
    return PM(561799,565833)


def Panda():
    return QtGui.QIcon(pmPanda())


def pmPenguin():
    return PM(565833,571382)


def Penguin():
    return QtGui.QIcon(pmPenguin())


def pmPig():
    return PM(571382,579422)


def Pig():
    return QtGui.QIcon(pmPig())


def pmRabbit():
    return PM(579422,586723)


def Rabbit():
    return QtGui.QIcon(pmRabbit())


def pmRhino():
    return PM(586723,593110)


def Rhino():
    return QtGui.QIcon(pmRhino())


def pmRooster():
    return PM(593110,598373)


def Rooster():
    return QtGui.QIcon(pmRooster())


def pmShark():
    return PM(598373,604143)


def Shark():
    return QtGui.QIcon(pmShark())


def pmSheep():
    return PM(604143,607974)


def Sheep():
    return QtGui.QIcon(pmSheep())


def pmSnake():
    return PM(607974,613999)


def Snake():
    return QtGui.QIcon(pmSnake())


def pmTiger():
    return PM(613999,622036)


def Tiger():
    return QtGui.QIcon(pmTiger())


def pmTurkey():
    return PM(622036,629450)


def Turkey():
    return QtGui.QIcon(pmTurkey())


def pmTurtle():
    return PM(629450,636171)


def Turtle():
    return QtGui.QIcon(pmTurtle())


def pmWolf():
    return PM(636171,639266)


def Wolf():
    return QtGui.QIcon(pmWolf())


def pmSteven():
    return PM(639266,646418)


def Steven():
    return QtGui.QIcon(pmSteven())


def pmWheel():
    return PM(646418,654483)


def Wheel():
    return QtGui.QIcon(pmWheel())


def pmWheelchair():
    return PM(654483,663287)


def Wheelchair():
    return QtGui.QIcon(pmWheelchair())


def pmTouringMotorcycle():
    return PM(663287,669599)


def TouringMotorcycle():
    return QtGui.QIcon(pmTouringMotorcycle())


def pmContainer():
    return PM(669599,674934)


def Container():
    return QtGui.QIcon(pmContainer())


def pmBoatEquipment():
    return PM(674934,680457)


def BoatEquipment():
    return QtGui.QIcon(pmBoatEquipment())


def pmCar():
    return PM(680457,685103)


def Car():
    return QtGui.QIcon(pmCar())


def pmLorry():
    return PM(685103,691139)


def Lorry():
    return QtGui.QIcon(pmLorry())


def pmCarTrailer():
    return PM(691139,695236)


def CarTrailer():
    return QtGui.QIcon(pmCarTrailer())


def pmTowTruck():
    return PM(695236,699994)


def TowTruck():
    return QtGui.QIcon(pmTowTruck())


def pmQuadBike():
    return PM(699994,705963)


def QuadBike():
    return QtGui.QIcon(pmQuadBike())


def pmRecoveryTruck():
    return PM(705963,710960)


def RecoveryTruck():
    return QtGui.QIcon(pmRecoveryTruck())


def pmContainerLoader():
    return PM(710960,716102)


def ContainerLoader():
    return QtGui.QIcon(pmContainerLoader())


def pmPoliceCar():
    return PM(716102,720934)


def PoliceCar():
    return QtGui.QIcon(pmPoliceCar())


def pmExecutiveCar():
    return PM(720934,725612)


def ExecutiveCar():
    return QtGui.QIcon(pmExecutiveCar())


def pmTruck():
    return PM(725612,731075)


def Truck():
    return QtGui.QIcon(pmTruck())


def pmExcavator():
    return PM(731075,735966)


def Excavator():
    return QtGui.QIcon(pmExcavator())


def pmCabriolet():
    return PM(735966,740804)


def Cabriolet():
    return QtGui.QIcon(pmCabriolet())


def pmMixerTruck():
    return PM(740804,747114)


def MixerTruck():
    return QtGui.QIcon(pmMixerTruck())


def pmForkliftTruckLoaded():
    return PM(747114,753262)


def ForkliftTruckLoaded():
    return QtGui.QIcon(pmForkliftTruckLoaded())


def pmAmbulance():
    return PM(753262,759312)


def Ambulance():
    return QtGui.QIcon(pmAmbulance())


def pmDieselLocomotiveBoxcar():
    return PM(759312,763318)


def DieselLocomotiveBoxcar():
    return QtGui.QIcon(pmDieselLocomotiveBoxcar())


def pmTractorUnit():
    return PM(763318,768785)


def TractorUnit():
    return QtGui.QIcon(pmTractorUnit())


def pmFireTruck():
    return PM(768785,775124)


def FireTruck():
    return QtGui.QIcon(pmFireTruck())


def pmCargoShip():
    return PM(775124,779465)


def CargoShip():
    return QtGui.QIcon(pmCargoShip())


def pmSubwayTrain():
    return PM(779465,784355)


def SubwayTrain():
    return QtGui.QIcon(pmSubwayTrain())


def pmTruckMountedCrane():
    return PM(784355,790096)


def TruckMountedCrane():
    return QtGui.QIcon(pmTruckMountedCrane())


def pmAirAmbulance():
    return PM(790096,795209)


def AirAmbulance():
    return QtGui.QIcon(pmAirAmbulance())


def pmAirplane():
    return PM(795209,800097)


def Airplane():
    return QtGui.QIcon(pmAirplane())


def pmCaracol():
    return PM(800097,801913)


def Caracol():
    return QtGui.QIcon(pmCaracol())


def pmUno():
    return PM(801913,804375)


def Uno():
    return QtGui.QIcon(pmUno())


def pmMotoresExternos():
    return PM(804375,806277)


def MotoresExternos():
    return QtGui.QIcon(pmMotoresExternos())


def pmDatabase():
    return PM(806277,807593)


def Database():
    return QtGui.QIcon(pmDatabase())


def pmDatabaseMas():
    return PM(807593,809052)


def DatabaseMas():
    return QtGui.QIcon(pmDatabaseMas())


def pmDatabaseImport():
    return PM(809052,809688)


def DatabaseImport():
    return QtGui.QIcon(pmDatabaseImport())


def pmDatabaseExport():
    return PM(809688,810333)


def DatabaseExport():
    return QtGui.QIcon(pmDatabaseExport())


def pmDatabaseDelete():
    return PM(810333,811456)


def DatabaseDelete():
    return QtGui.QIcon(pmDatabaseDelete())


def pmDatabaseMaintenance():
    return PM(811456,812952)


def DatabaseMaintenance():
    return QtGui.QIcon(pmDatabaseMaintenance())


def pmAtacante():
    return PM(812952,813557)


def Atacante():
    return QtGui.QIcon(pmAtacante())


def pmAtacada():
    return PM(813557,814123)


def Atacada():
    return QtGui.QIcon(pmAtacada())


def pmGoToNext():
    return PM(814123,814535)


def GoToNext():
    return QtGui.QIcon(pmGoToNext())


def pmBlancas():
    return PM(814535,814886)


def Blancas():
    return QtGui.QIcon(pmBlancas())


def pmNegras():
    return PM(814886,815132)


def Negras():
    return QtGui.QIcon(pmNegras())


def pmFolderChange():
    return PM(69940,72698)


def FolderChange():
    return QtGui.QIcon(pmFolderChange())


def pmMarkers():
    return PM(815132,816827)


def Markers():
    return QtGui.QIcon(pmMarkers())


def pmTop():
    return PM(816827,817411)


def Top():
    return QtGui.QIcon(pmTop())


def pmBottom():
    return PM(817411,818000)


def Bottom():
    return QtGui.QIcon(pmBottom())


def pmSTS():
    return PM(818000,820191)


def STS():
    return QtGui.QIcon(pmSTS())


def pmRun():
    return PM(820191,821915)


def Run():
    return QtGui.QIcon(pmRun())


def pmRun2():
    return PM(821915,823435)


def Run2():
    return QtGui.QIcon(pmRun2())


def pmWorldMap():
    return PM(823435,826176)


def WorldMap():
    return QtGui.QIcon(pmWorldMap())


def pmAfrica():
    return PM(826176,828662)


def Africa():
    return QtGui.QIcon(pmAfrica())


def pmMaps():
    return PM(828662,829606)


def Maps():
    return QtGui.QIcon(pmMaps())


def pmSol():
    return PM(829606,830532)


def Sol():
    return QtGui.QIcon(pmSol())


def pmSolNubes():
    return PM(830532,831395)


def SolNubes():
    return QtGui.QIcon(pmSolNubes())


def pmSolNubesLluvia():
    return PM(831395,832355)


def SolNubesLluvia():
    return QtGui.QIcon(pmSolNubesLluvia())


def pmLluvia():
    return PM(832355,833194)


def Lluvia():
    return QtGui.QIcon(pmLluvia())


def pmInvierno():
    return PM(833194,834770)


def Invierno():
    return QtGui.QIcon(pmInvierno())


def pmFixedElo():
    return PM(163257,164520)


def FixedElo():
    return QtGui.QIcon(pmFixedElo())


def pmSoundTool():
    return PM(834770,837229)


def SoundTool():
    return QtGui.QIcon(pmSoundTool())


def pmTrain():
    return PM(837229,838599)


def Train():
    return QtGui.QIcon(pmTrain())


def pmPlay():
    return PM(229462,231551)


def Play():
    return QtGui.QIcon(pmPlay())


def pmMeasure():
    return PM(125042,126665)


def Measure():
    return QtGui.QIcon(pmMeasure())


def pmPlayGame():
    return PM(838599,842957)


def PlayGame():
    return QtGui.QIcon(pmPlayGame())


def pmScanner():
    return PM(842957,843298)


def Scanner():
    return QtGui.QIcon(pmScanner())


def pmCursorScanner():
    return PM(843298,843615)


def CursorScanner():
    return QtGui.QIcon(pmCursorScanner())


def pmMenos():
    return PM(843615,844140)


def Menos():
    return QtGui.QIcon(pmMenos())


def pmSchool():
    return PM(844140,845502)


def School():
    return QtGui.QIcon(pmSchool())


def pmLaw():
    return PM(845502,846118)


def Law():
    return QtGui.QIcon(pmLaw())


def pmLearnGame():
    return PM(846118,846551)


def LearnGame():
    return QtGui.QIcon(pmLearnGame())


def pmLonghaul():
    return PM(846551,847477)


def Longhaul():
    return QtGui.QIcon(pmLonghaul())


def pmTrekking():
    return PM(847477,848171)


def Trekking():
    return QtGui.QIcon(pmTrekking())


def pmPassword():
    return PM(848171,848624)


def Password():
    return QtGui.QIcon(pmPassword())


def pmSQL_RAW():
    return PM(838599,842957)


def SQL_RAW():
    return QtGui.QIcon(pmSQL_RAW())


def pmSun():
    return PM(308686,309564)


def Sun():
    return QtGui.QIcon(pmSun())


def pmLight32():
    return PM(848624,850324)


def Light32():
    return QtGui.QIcon(pmLight32())


def pmTOL():
    return PM(850324,851033)


def TOL():
    return QtGui.QIcon(pmTOL())


def pmUned():
    return PM(851033,851453)


def Uned():
    return QtGui.QIcon(pmUned())


def pmUwe():
    return PM(851453,852422)


def Uwe():
    return QtGui.QIcon(pmUwe())


def pmThinking():
    return PM(852422,853211)


def Thinking():
    return QtGui.QIcon(pmThinking())


def pmWashingMachine():
    return PM(853211,853874)


def WashingMachine():
    return QtGui.QIcon(pmWashingMachine())


def pmTerminal():
    return PM(853874,857418)


def Terminal():
    return QtGui.QIcon(pmTerminal())


def pmManualSave():
    return PM(857418,858001)


def ManualSave():
    return QtGui.QIcon(pmManualSave())


def pmSettings():
    return PM(858001,858439)


def Settings():
    return QtGui.QIcon(pmSettings())


def pmStrength():
    return PM(858439,859110)


def Strength():
    return QtGui.QIcon(pmStrength())


def pmSingular():
    return PM(859110,859965)


def Singular():
    return QtGui.QIcon(pmSingular())


def pmScript():
    return PM(859965,860534)


def Script():
    return QtGui.QIcon(pmScript())


def pmTexto():
    return PM(860534,863379)


def Texto():
    return QtGui.QIcon(pmTexto())


def pmLampara():
    return PM(863379,864088)


def Lampara():
    return QtGui.QIcon(pmLampara())


def pmFile():
    return PM(864088,866388)


def File():
    return QtGui.QIcon(pmFile())


def pmCalculo():
    return PM(866388,867314)


def Calculo():
    return QtGui.QIcon(pmCalculo())


def pmOpeningLines():
    return PM(867314,867992)


def OpeningLines():
    return QtGui.QIcon(pmOpeningLines())


def pmStudy():
    return PM(867992,868905)


def Study():
    return QtGui.QIcon(pmStudy())


def pmLichess():
    return PM(868905,869793)


def Lichess():
    return QtGui.QIcon(pmLichess())


def pmMiniatura():
    return PM(869793,870720)


def Miniatura():
    return QtGui.QIcon(pmMiniatura())


def pmLocomotora():
    return PM(870720,871501)


def Locomotora():
    return QtGui.QIcon(pmLocomotora())


def pmTrainSequential():
    return PM(871501,872642)


def TrainSequential():
    return QtGui.QIcon(pmTrainSequential())


def pmTrainStatic():
    return PM(872642,873602)


def TrainStatic():
    return QtGui.QIcon(pmTrainStatic())


def pmTrainPositions():
    return PM(873602,874583)


def TrainPositions():
    return QtGui.QIcon(pmTrainPositions())


def pmTrainEngines():
    return PM(874583,876017)


def TrainEngines():
    return QtGui.QIcon(pmTrainEngines())


def pmError():
    return PM(47124,51124)


def Error():
    return QtGui.QIcon(pmError())


def pmAtajos():
    return PM(876017,877196)


def Atajos():
    return QtGui.QIcon(pmAtajos())


def pmTOLline():
    return PM(877196,878300)


def TOLline():
    return QtGui.QIcon(pmTOLline())


def pmTOLchange():
    return PM(878300,880522)


def TOLchange():
    return QtGui.QIcon(pmTOLchange())


def pmPack():
    return PM(880522,881695)


def Pack():
    return QtGui.QIcon(pmPack())


def pmHome():
    return PM(178267,179449)


def Home():
    return QtGui.QIcon(pmHome())


def pmImport8():
    return PM(881695,882453)


def Import8():
    return QtGui.QIcon(pmImport8())


def pmExport8():
    return PM(882453,883078)


def Export8():
    return QtGui.QIcon(pmExport8())


def pmTablas8():
    return PM(883078,883870)


def Tablas8():
    return QtGui.QIcon(pmTablas8())


def pmBlancas8():
    return PM(883870,884900)


def Blancas8():
    return QtGui.QIcon(pmBlancas8())


def pmNegras8():
    return PM(884900,885739)


def Negras8():
    return QtGui.QIcon(pmNegras8())


def pmBook():
    return PM(885739,886313)


def Book():
    return QtGui.QIcon(pmBook())


def pmWrite():
    return PM(886313,887518)


def Write():
    return QtGui.QIcon(pmWrite())


def pmAlt():
    return PM(887518,887960)


def Alt():
    return QtGui.QIcon(pmAlt())


def pmShift():
    return PM(887960,888300)


def Shift():
    return QtGui.QIcon(pmShift())


def pmRightMouse():
    return PM(888300,889100)


def RightMouse():
    return QtGui.QIcon(pmRightMouse())


def pmControl():
    return PM(889100,889625)


def Control():
    return QtGui.QIcon(pmControl())


def pmFinales():
    return PM(889625,890712)


def Finales():
    return QtGui.QIcon(pmFinales())


def pmEditColumns():
    return PM(890712,891444)


def EditColumns():
    return QtGui.QIcon(pmEditColumns())


def pmResizeAll():
    return PM(891444,891954)


def ResizeAll():
    return QtGui.QIcon(pmResizeAll())


def pmChecked():
    return PM(891954,892460)


def Checked():
    return QtGui.QIcon(pmChecked())


def pmUnchecked():
    return PM(892460,892708)


def Unchecked():
    return QtGui.QIcon(pmUnchecked())


def pmBuscarC():
    return PM(892708,893152)


def BuscarC():
    return QtGui.QIcon(pmBuscarC())


def pmPeonBlanco():
    return PM(893152,895333)


def PeonBlanco():
    return QtGui.QIcon(pmPeonBlanco())


def pmPeonNegro():
    return PM(895333,896857)


def PeonNegro():
    return QtGui.QIcon(pmPeonNegro())


def pmReciclar():
    return PM(896857,897581)


def Reciclar():
    return QtGui.QIcon(pmReciclar())


def pmLanzamiento():
    return PM(897581,898294)


def Lanzamiento():
    return QtGui.QIcon(pmLanzamiento())


def pmEndGame():
    return PM(898294,898708)


def EndGame():
    return QtGui.QIcon(pmEndGame())


def pmPause():
    return PM(898708,899577)


def Pause():
    return QtGui.QIcon(pmPause())


def pmContinue():
    return PM(899577,900781)


def Continue():
    return QtGui.QIcon(pmContinue())


def pmClose():
    return PM(900781,901480)


def Close():
    return QtGui.QIcon(pmClose())


def pmStop():
    return PM(901480,902513)


def Stop():
    return QtGui.QIcon(pmStop())


def pmFactoryPolyglot():
    return PM(902513,903333)


def FactoryPolyglot():
    return QtGui.QIcon(pmFactoryPolyglot())


def pmTags():
    return PM(903333,904156)


def Tags():
    return QtGui.QIcon(pmTags())


def pmAppearance():
    return PM(904156,904883)


def Appearance():
    return QtGui.QIcon(pmAppearance())


def pmFill():
    return PM(904883,905921)


def Fill():
    return QtGui.QIcon(pmFill())


def pmSupport():
    return PM(905921,906653)


def Support():
    return QtGui.QIcon(pmSupport())


def pmOrder():
    return PM(906653,907451)


def Order():
    return QtGui.QIcon(pmOrder())


def pmPlay1():
    return PM(907451,908746)


def Play1():
    return QtGui.QIcon(pmPlay1())


def pmRemove1():
    return PM(908746,909873)


def Remove1():
    return QtGui.QIcon(pmRemove1())


def pmNew1():
    return PM(909873,910195)


def New1():
    return QtGui.QIcon(pmNew1())


def pmMensError():
    return PM(910195,912259)


def MensError():
    return QtGui.QIcon(pmMensError())


def pmMensInfo():
    return PM(912259,914814)


def MensInfo():
    return QtGui.QIcon(pmMensInfo())


def pmJump():
    return PM(914814,915489)


def Jump():
    return QtGui.QIcon(pmJump())


def pmCaptures():
    return PM(915489,916670)


def Captures():
    return QtGui.QIcon(pmCaptures())


def pmRepeat():
    return PM(916670,917329)


def Repeat():
    return QtGui.QIcon(pmRepeat())


def pmCount():
    return PM(917329,918005)


def Count():
    return QtGui.QIcon(pmCount())


def pmMate15():
    return PM(918005,919076)


def Mate15():
    return QtGui.QIcon(pmMate15())


def pmCoordinates():
    return PM(919076,920229)


def Coordinates():
    return QtGui.QIcon(pmCoordinates())


def pmKnight():
    return PM(920229,921472)


def Knight():
    return QtGui.QIcon(pmKnight())


def pmCorrecto():
    return PM(921472,922498)


def Correcto():
    return QtGui.QIcon(pmCorrecto())


def pmBlocks():
    return PM(922498,922835)


def Blocks():
    return QtGui.QIcon(pmBlocks())


def pmWest():
    return PM(922835,923941)


def West():
    return QtGui.QIcon(pmWest())


def pmOpening():
    return PM(923941,924199)


def Opening():
    return QtGui.QIcon(pmOpening())


def pmVariation():
    return PM(220802,221220)


def Variation():
    return QtGui.QIcon(pmVariation())


def pmComment():
    return PM(924199,924562)


def Comment():
    return QtGui.QIcon(pmComment())


def pmVariationComment():
    return PM(924562,924906)


def VariationComment():
    return QtGui.QIcon(pmVariationComment())


def pmOpeningVariation():
    return PM(924906,925370)


def OpeningVariation():
    return QtGui.QIcon(pmOpeningVariation())


def pmOpeningComment():
    return PM(925370,925703)


def OpeningComment():
    return QtGui.QIcon(pmOpeningComment())


def pmOpeningVariationComment():
    return PM(924906,925370)


def OpeningVariationComment():
    return QtGui.QIcon(pmOpeningVariationComment())


def pmDeleteRow():
    return PM(925703,926134)


def DeleteRow():
    return QtGui.QIcon(pmDeleteRow())


def pmDeleteColumn():
    return PM(926134,926577)


def DeleteColumn():
    return QtGui.QIcon(pmDeleteColumn())


def pmEditVariation():
    return PM(926577,926932)


def EditVariation():
    return QtGui.QIcon(pmEditVariation())


def pmKibitzer():
    return PM(926932,927531)


def Kibitzer():
    return QtGui.QIcon(pmKibitzer())


def pmKibitzer_Pause():
    return PM(927531,927703)


def Kibitzer_Pause():
    return QtGui.QIcon(pmKibitzer_Pause())


def pmKibitzer_Options():
    return PM(927703,928605)


def Kibitzer_Options():
    return QtGui.QIcon(pmKibitzer_Options())


def pmKibitzer_Voyager():
    return PM(343531,344374)


def Kibitzer_Voyager():
    return QtGui.QIcon(pmKibitzer_Voyager())


def pmKibitzer_Close():
    return PM(928605,929162)


def Kibitzer_Close():
    return QtGui.QIcon(pmKibitzer_Close())


def pmKibitzer_Down():
    return PM(929162,929551)


def Kibitzer_Down():
    return QtGui.QIcon(pmKibitzer_Down())


def pmKibitzer_Up():
    return PM(929551,929946)


def Kibitzer_Up():
    return QtGui.QIcon(pmKibitzer_Up())


def pmKibitzer_Back():
    return PM(929946,930379)


def Kibitzer_Back():
    return QtGui.QIcon(pmKibitzer_Back())


def pmKibitzer_Clipboard():
    return PM(930379,930765)


def Kibitzer_Clipboard():
    return QtGui.QIcon(pmKibitzer_Clipboard())


def pmKibitzer_Play():
    return PM(930765,931286)


def Kibitzer_Play():
    return QtGui.QIcon(pmKibitzer_Play())


def pmKibitzer_Side():
    return PM(931286,932039)


def Kibitzer_Side():
    return QtGui.QIcon(pmKibitzer_Side())


def pmKibitzer_Board():
    return PM(932039,932477)


def Kibitzer_Board():
    return QtGui.QIcon(pmKibitzer_Board())


def pmBoard():
    return PM(932477,932946)


def Board():
    return QtGui.QIcon(pmBoard())


def pmTraining_Games():
    return PM(932946,934638)


def Training_Games():
    return QtGui.QIcon(pmTraining_Games())


def pmTraining_Basic():
    return PM(934638,936011)


def Training_Basic():
    return QtGui.QIcon(pmTraining_Basic())


def pmTraining_Tactics():
    return PM(936011,936792)


def Training_Tactics():
    return QtGui.QIcon(pmTraining_Tactics())


def pmTraining_Endings():
    return PM(936792,937726)


def Training_Endings():
    return QtGui.QIcon(pmTraining_Endings())


def pmBridge():
    return PM(937726,938744)


def Bridge():
    return QtGui.QIcon(pmBridge())


def pmMaia():
    return PM(938744,939528)


def Maia():
    return QtGui.QIcon(pmMaia())


def pmBinBook():
    return PM(939528,940277)


def BinBook():
    return QtGui.QIcon(pmBinBook())


def pmConnected():
    return PM(940277,941895)


def Connected():
    return QtGui.QIcon(pmConnected())


def pmThemes():
    return PM(941895,942464)


def Themes():
    return QtGui.QIcon(pmThemes())


def pmReset():
    return PM(942464,944083)


def Reset():
    return QtGui.QIcon(pmReset())


def pmInstall():
    return PM(944083,946212)


def Install():
    return QtGui.QIcon(pmInstall())


def pmUninstall():
    return PM(946212,948238)


def Uninstall():
    return QtGui.QIcon(pmUninstall())


def pmLive():
    return PM(948238,951721)


def Live():
    return QtGui.QIcon(pmLive())


def pmLauncher():
    return PM(951721,956396)


def Launcher():
    return QtGui.QIcon(pmLauncher())


def pmLogInactive():
    return PM(956396,956927)


def LogInactive():
    return QtGui.QIcon(pmLogInactive())


def pmLogActive():
    return PM(956927,957491)


def LogActive():
    return QtGui.QIcon(pmLogActive())


def pmFolderAnil():
    return PM(957491,957855)


def FolderAnil():
    return QtGui.QIcon(pmFolderAnil())


def pmFolderBlack():
    return PM(957855,958192)


def FolderBlack():
    return QtGui.QIcon(pmFolderBlack())


def pmFolderBlue():
    return PM(958192,958566)


def FolderBlue():
    return QtGui.QIcon(pmFolderBlue())


def pmFolderGreen():
    return PM(958566,958938)


def FolderGreen():
    return QtGui.QIcon(pmFolderGreen())


def pmFolderMagenta():
    return PM(958938,959311)


def FolderMagenta():
    return QtGui.QIcon(pmFolderMagenta())


def pmFolderRed():
    return PM(959311,959675)


def FolderRed():
    return QtGui.QIcon(pmFolderRed())


def pmThis():
    return PM(959675,960129)


def This():
    return QtGui.QIcon(pmThis())


def pmAll():
    return PM(960129,960632)


def All():
    return QtGui.QIcon(pmAll())


def pmPrevious():
    return PM(960632,961091)


def Previous():
    return QtGui.QIcon(pmPrevious())


def pmLine():
    return PM(961091,961278)


def Line():
    return QtGui.QIcon(pmLine())


def pmEmpty():
    return PM(961278,961363)


def Empty():
    return QtGui.QIcon(pmEmpty())


def pmMore():
    return PM(961363,961652)


def More():
    return QtGui.QIcon(pmMore())


def pmSelectLogo():
    return PM(961652,962258)


def SelectLogo():
    return QtGui.QIcon(pmSelectLogo())


def pmSelect():
    return PM(962258,962912)


def Select():
    return QtGui.QIcon(pmSelect())


def pmSelectClose():
    return PM(962912,963684)


def SelectClose():
    return QtGui.QIcon(pmSelectClose())


def pmSelectHome():
    return PM(963684,964466)


def SelectHome():
    return QtGui.QIcon(pmSelectHome())


def pmSelectHistory():
    return PM(964466,965018)


def SelectHistory():
    return QtGui.QIcon(pmSelectHistory())


def pmSelectExplorer():
    return PM(965018,965751)


def SelectExplorer():
    return QtGui.QIcon(pmSelectExplorer())


def pmSelectFolderCreate():
    return PM(965751,966670)


def SelectFolderCreate():
    return QtGui.QIcon(pmSelectFolderCreate())


def pmSelectFolderRemove():
    return PM(966670,967697)


def SelectFolderRemove():
    return QtGui.QIcon(pmSelectFolderRemove())


def pmSelectReload():
    return PM(967697,969351)


def SelectReload():
    return QtGui.QIcon(pmSelectReload())


def pmSelectAccept():
    return PM(969351,970152)


def SelectAccept():
    return QtGui.QIcon(pmSelectAccept())


def pmWiki():
    return PM(970152,971269)


def Wiki():
    return QtGui.QIcon(pmWiki())


def pmCircle():
    return PM(971269,972729)


def Circle():
    return QtGui.QIcon(pmCircle())


def pmSortAZ():
    return PM(972729,973493)


def SortAZ():
    return QtGui.QIcon(pmSortAZ())


def pmReference():
    return PM(973493,974604)


def Reference():
    return QtGui.QIcon(pmReference())


def pmLanguageNew():
    return PM(974604,975331)


def LanguageNew():
    return QtGui.QIcon(pmLanguageNew())


def pmODT():
    return PM(975331,976446)


def ODT():
    return QtGui.QIcon(pmODT())


def pmEngines():
    return PM(976446,977932)


def Engines():
    return QtGui.QIcon(pmEngines())


def pmConfEngines():
    return PM(977932,979128)


def ConfEngines():
    return QtGui.QIcon(pmConfEngines())


def pmEngine():
    return PM(979128,980552)


def Engine():
    return QtGui.QIcon(pmEngine())


def pmZip():
    return PM(980552,981448)


def Zip():
    return QtGui.QIcon(pmZip())


def pmUpdate():
    return PM(981448,982532)


def Update():
    return QtGui.QIcon(pmUpdate())


