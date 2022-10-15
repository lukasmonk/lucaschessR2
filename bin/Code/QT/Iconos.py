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


def pmFindAllMoves():
    return PM(11623,13219)


def FindAllMoves():
    return QtGui.QIcon(pmFindAllMoves())


def pmResizeBoard():
    return PM(11623,13219)


def ResizeBoard():
    return QtGui.QIcon(pmResizeBoard())


def pmMensEspera():
    return PM(13219,16967)


def MensEspera():
    return QtGui.QIcon(pmMensEspera())


def pmUtilidades():
    return PM(16967,23396)


def Utilidades():
    return QtGui.QIcon(pmUtilidades())


def pmTerminar():
    return PM(23396,25146)


def Terminar():
    return QtGui.QIcon(pmTerminar())


def pmNuevaPartida():
    return PM(25146,26894)


def NuevaPartida():
    return QtGui.QIcon(pmNuevaPartida())


def pmOpciones():
    return PM(26894,28622)


def Opciones():
    return QtGui.QIcon(pmOpciones())


def pmEntrenamiento():
    return PM(7617,9646)


def Entrenamiento():
    return QtGui.QIcon(pmEntrenamiento())


def pmAplazar():
    return PM(28622,31689)


def Aplazar():
    return QtGui.QIcon(pmAplazar())


def pmAplazamientos():
    return PM(31689,35005)


def Aplazamientos():
    return QtGui.QIcon(pmAplazamientos())


def pmCapturas():
    return PM(35005,37046)


def Capturas():
    return QtGui.QIcon(pmCapturas())


def pmReiniciar():
    return PM(37046,39340)


def Reiniciar():
    return QtGui.QIcon(pmReiniciar())


def pmImportarGM():
    return PM(39340,41940)


def ImportarGM():
    return QtGui.QIcon(pmImportarGM())


def pmAbandonar():
    return PM(41940,45940)


def Abandonar():
    return QtGui.QIcon(pmAbandonar())


def pmEmpezar():
    return PM(45940,47976)


def Empezar():
    return QtGui.QIcon(pmEmpezar())


def pmOtros():
    return PM(47976,52446)


def Otros():
    return QtGui.QIcon(pmOtros())


def pmAnalizar():
    return PM(52446,54055)


def Analizar():
    return QtGui.QIcon(pmAnalizar())


def pmConfAnalysis():
    return PM(54055,54878)


def ConfAnalysis():
    return QtGui.QIcon(pmConfAnalysis())


def pmMainMenu():
    return PM(54878,59188)


def MainMenu():
    return QtGui.QIcon(pmMainMenu())


def pmFinPartida():
    return PM(59188,62136)


def FinPartida():
    return QtGui.QIcon(pmFinPartida())


def pmGrabar():
    return PM(62136,63599)


def Grabar():
    return QtGui.QIcon(pmGrabar())


def pmGrabarComo():
    return PM(63599,65651)


def GrabarComo():
    return QtGui.QIcon(pmGrabarComo())


def pmRecuperar():
    return PM(65651,68409)


def Recuperar():
    return QtGui.QIcon(pmRecuperar())


def pmInformacion():
    return PM(68409,70368)


def Informacion():
    return QtGui.QIcon(pmInformacion())


def pmNuevo():
    return PM(70368,71122)


def Nuevo():
    return QtGui.QIcon(pmNuevo())


def pmCopiar():
    return PM(71122,72303)


def Copiar():
    return QtGui.QIcon(pmCopiar())


def pmModificar():
    return PM(72303,76700)


def Modificar():
    return QtGui.QIcon(pmModificar())


def pmBorrar():
    return PM(76700,81691)


def Borrar():
    return QtGui.QIcon(pmBorrar())


def pmMarcar():
    return PM(81691,86620)


def Marcar():
    return QtGui.QIcon(pmMarcar())


def pmPegar():
    return PM(86620,88931)


def Pegar():
    return QtGui.QIcon(pmPegar())


def pmFichero():
    return PM(88931,93616)


def Fichero():
    return QtGui.QIcon(pmFichero())


def pmNuestroFichero():
    return PM(93616,96663)


def NuestroFichero():
    return QtGui.QIcon(pmNuestroFichero())


def pmFicheroRepite():
    return PM(96663,98159)


def FicheroRepite():
    return QtGui.QIcon(pmFicheroRepite())


def pmInformacionPGN():
    return PM(98159,99177)


def InformacionPGN():
    return QtGui.QIcon(pmInformacionPGN())


def pmVer():
    return PM(99177,100631)


def Ver():
    return QtGui.QIcon(pmVer())


def pmInicio():
    return PM(100631,102645)


def Inicio():
    return QtGui.QIcon(pmInicio())


def pmFinal():
    return PM(102645,104639)


def Final():
    return QtGui.QIcon(pmFinal())


def pmFiltrar():
    return PM(104639,111129)


def Filtrar():
    return QtGui.QIcon(pmFiltrar())


def pmArriba():
    return PM(111129,113282)


def Arriba():
    return QtGui.QIcon(pmArriba())


def pmAbajo():
    return PM(113282,115390)


def Abajo():
    return QtGui.QIcon(pmAbajo())


def pmEstadisticas():
    return PM(115390,117529)


def Estadisticas():
    return QtGui.QIcon(pmEstadisticas())


def pmCheck():
    return PM(117529,120753)


def Check():
    return QtGui.QIcon(pmCheck())


def pmTablas():
    return PM(120753,122376)


def Tablas():
    return QtGui.QIcon(pmTablas())


def pmAtras():
    return PM(122376,123895)


def Atras():
    return QtGui.QIcon(pmAtras())


def pmBuscar():
    return PM(123895,125880)


def Buscar():
    return QtGui.QIcon(pmBuscar())


def pmLibros():
    return PM(125880,128008)


def Libros():
    return QtGui.QIcon(pmLibros())


def pmAceptar():
    return PM(128008,131355)


def Aceptar():
    return QtGui.QIcon(pmAceptar())


def pmCancelar():
    return PM(131355,133338)


def Cancelar():
    return QtGui.QIcon(pmCancelar())


def pmDefecto():
    return PM(133338,136657)


def Defecto():
    return QtGui.QIcon(pmDefecto())


def pmInsertar():
    return PM(136657,139053)


def Insertar():
    return QtGui.QIcon(pmInsertar())


def pmJugar():
    return PM(139053,141262)


def Jugar():
    return QtGui.QIcon(pmJugar())


def pmConfigurar():
    return PM(141262,144346)


def Configurar():
    return QtGui.QIcon(pmConfigurar())


def pmS_Aceptar():
    return PM(128008,131355)


def S_Aceptar():
    return QtGui.QIcon(pmS_Aceptar())


def pmS_Cancelar():
    return PM(131355,133338)


def S_Cancelar():
    return QtGui.QIcon(pmS_Cancelar())


def pmS_Microfono():
    return PM(144346,149787)


def S_Microfono():
    return QtGui.QIcon(pmS_Microfono())


def pmS_LeerWav():
    return PM(39340,41940)


def S_LeerWav():
    return QtGui.QIcon(pmS_LeerWav())


def pmS_Play():
    return PM(149787,155125)


def S_Play():
    return QtGui.QIcon(pmS_Play())


def pmS_StopPlay():
    return PM(155125,155735)


def S_StopPlay():
    return QtGui.QIcon(pmS_StopPlay())


def pmS_StopMicrofono():
    return PM(155125,155735)


def S_StopMicrofono():
    return QtGui.QIcon(pmS_StopMicrofono())


def pmS_Record():
    return PM(155735,158968)


def S_Record():
    return QtGui.QIcon(pmS_Record())


def pmS_Limpiar():
    return PM(76700,81691)


def S_Limpiar():
    return QtGui.QIcon(pmS_Limpiar())


def pmHistorial():
    return PM(158968,160231)


def Historial():
    return QtGui.QIcon(pmHistorial())


def pmPegar16():
    return PM(160231,161225)


def Pegar16():
    return QtGui.QIcon(pmPegar16())


def pmRivalesMP():
    return PM(161225,163907)


def RivalesMP():
    return QtGui.QIcon(pmRivalesMP())


def pmCamara():
    return PM(163907,165429)


def Camara():
    return QtGui.QIcon(pmCamara())


def pmUsuarios():
    return PM(165429,166669)


def Usuarios():
    return QtGui.QIcon(pmUsuarios())


def pmResistencia():
    return PM(166669,169731)


def Resistencia():
    return QtGui.QIcon(pmResistencia())


def pmCebra():
    return PM(169731,172184)


def Cebra():
    return QtGui.QIcon(pmCebra())


def pmGafas():
    return PM(172184,173342)


def Gafas():
    return QtGui.QIcon(pmGafas())


def pmPuente():
    return PM(173342,173978)


def Puente():
    return QtGui.QIcon(pmPuente())


def pmWeb():
    return PM(173978,175160)


def Web():
    return QtGui.QIcon(pmWeb())


def pmMail():
    return PM(175160,176120)


def Mail():
    return QtGui.QIcon(pmMail())


def pmAyuda():
    return PM(176120,177301)


def Ayuda():
    return QtGui.QIcon(pmAyuda())


def pmFAQ():
    return PM(177301,178622)


def FAQ():
    return QtGui.QIcon(pmFAQ())


def pmActualiza():
    return PM(178622,179488)


def Actualiza():
    return QtGui.QIcon(pmActualiza())


def pmRefresh():
    return PM(179488,181880)


def Refresh():
    return QtGui.QIcon(pmRefresh())


def pmJuegaSolo():
    return PM(181880,183732)


def JuegaSolo():
    return QtGui.QIcon(pmJuegaSolo())


def pmPlayer():
    return PM(183732,184914)


def Player():
    return QtGui.QIcon(pmPlayer())


def pmJS_Rotacion():
    return PM(184914,186824)


def JS_Rotacion():
    return QtGui.QIcon(pmJS_Rotacion())


def pmElo():
    return PM(186824,188330)


def Elo():
    return QtGui.QIcon(pmElo())


def pmMate():
    return PM(188330,188891)


def Mate():
    return QtGui.QIcon(pmMate())


def pmEloTimed():
    return PM(188891,190375)


def EloTimed():
    return QtGui.QIcon(pmEloTimed())


def pmPGN():
    return PM(190375,192373)


def PGN():
    return QtGui.QIcon(pmPGN())


def pmPGN_Importar():
    return PM(192373,193963)


def PGN_Importar():
    return QtGui.QIcon(pmPGN_Importar())


def pmAyudaGR():
    return PM(193963,199841)


def AyudaGR():
    return QtGui.QIcon(pmAyudaGR())


def pmBotonAyuda():
    return PM(199841,202301)


def BotonAyuda():
    return QtGui.QIcon(pmBotonAyuda())


def pmColores():
    return PM(202301,203532)


def Colores():
    return QtGui.QIcon(pmColores())


def pmEditarColores():
    return PM(203532,205835)


def EditarColores():
    return QtGui.QIcon(pmEditarColores())


def pmGranMaestro():
    return PM(205835,206691)


def GranMaestro():
    return QtGui.QIcon(pmGranMaestro())


def pmFavoritos():
    return PM(206691,208457)


def Favoritos():
    return QtGui.QIcon(pmFavoritos())


def pmCarpeta():
    return PM(208457,209161)


def Carpeta():
    return QtGui.QIcon(pmCarpeta())


def pmDivision():
    return PM(209161,209826)


def Division():
    return QtGui.QIcon(pmDivision())


def pmDivisionF():
    return PM(209826,210940)


def DivisionF():
    return QtGui.QIcon(pmDivisionF())


def pmDelete():
    return PM(210940,211864)


def Delete():
    return QtGui.QIcon(pmDelete())


def pmModificarP():
    return PM(211864,212930)


def ModificarP():
    return QtGui.QIcon(pmModificarP())


def pmGrupo_Si():
    return PM(212930,213392)


def Grupo_Si():
    return QtGui.QIcon(pmGrupo_Si())


def pmGrupo_No():
    return PM(213392,213715)


def Grupo_No():
    return QtGui.QIcon(pmGrupo_No())


def pmMotor_Si():
    return PM(213715,214177)


def Motor_Si():
    return QtGui.QIcon(pmMotor_Si())


def pmMotor_No():
    return PM(210940,211864)


def Motor_No():
    return QtGui.QIcon(pmMotor_No())


def pmMotor_Actual():
    return PM(214177,215194)


def Motor_Actual():
    return QtGui.QIcon(pmMotor_Actual())


def pmMoverInicio():
    return PM(215194,215492)


def MoverInicio():
    return QtGui.QIcon(pmMoverInicio())


def pmMoverFinal():
    return PM(215492,215793)


def MoverFinal():
    return QtGui.QIcon(pmMoverFinal())


def pmMoverAdelante():
    return PM(215793,216148)


def MoverAdelante():
    return QtGui.QIcon(pmMoverAdelante())


def pmMoverAtras():
    return PM(216148,216513)


def MoverAtras():
    return QtGui.QIcon(pmMoverAtras())


def pmMoverLibre():
    return PM(216513,216931)


def MoverLibre():
    return QtGui.QIcon(pmMoverLibre())


def pmMoverTiempo():
    return PM(216931,217510)


def MoverTiempo():
    return QtGui.QIcon(pmMoverTiempo())


def pmMoverMas():
    return PM(217510,218549)


def MoverMas():
    return QtGui.QIcon(pmMoverMas())


def pmMoverGrabar():
    return PM(218549,219405)


def MoverGrabar():
    return QtGui.QIcon(pmMoverGrabar())


def pmMoverGrabarTodos():
    return PM(219405,220449)


def MoverGrabarTodos():
    return QtGui.QIcon(pmMoverGrabarTodos())


def pmMoverJugar():
    return PM(220449,221280)


def MoverJugar():
    return QtGui.QIcon(pmMoverJugar())


def pmPelicula():
    return PM(221280,223414)


def Pelicula():
    return QtGui.QIcon(pmPelicula())


def pmPelicula_Pausa():
    return PM(223414,225173)


def Pelicula_Pausa():
    return QtGui.QIcon(pmPelicula_Pausa())


def pmPelicula_Seguir():
    return PM(225173,227262)


def Pelicula_Seguir():
    return QtGui.QIcon(pmPelicula_Seguir())


def pmPelicula_Rapido():
    return PM(227262,229321)


def Pelicula_Rapido():
    return QtGui.QIcon(pmPelicula_Rapido())


def pmPelicula_Lento():
    return PM(229321,231196)


def Pelicula_Lento():
    return QtGui.QIcon(pmPelicula_Lento())


def pmPelicula_Repetir():
    return PM(37046,39340)


def Pelicula_Repetir():
    return QtGui.QIcon(pmPelicula_Repetir())


def pmPelicula_PGN():
    return PM(231196,232104)


def Pelicula_PGN():
    return QtGui.QIcon(pmPelicula_PGN())


def pmMemoria():
    return PM(232104,234045)


def Memoria():
    return QtGui.QIcon(pmMemoria())


def pmEntrenar():
    return PM(234045,235584)


def Entrenar():
    return QtGui.QIcon(pmEntrenar())


def pmEnviar():
    return PM(234045,235584)


def Enviar():
    return QtGui.QIcon(pmEnviar())


def pmBoxRooms():
    return PM(235584,240387)


def BoxRooms():
    return QtGui.QIcon(pmBoxRooms())


def pmBoxRoom():
    return PM(240387,240849)


def BoxRoom():
    return QtGui.QIcon(pmBoxRoom())


def pmNewBoxRoom():
    return PM(240849,242357)


def NewBoxRoom():
    return QtGui.QIcon(pmNewBoxRoom())


def pmNuevoMas():
    return PM(240849,242357)


def NuevoMas():
    return QtGui.QIcon(pmNuevoMas())


def pmTemas():
    return PM(242357,244580)


def Temas():
    return QtGui.QIcon(pmTemas())


def pmTutorialesCrear():
    return PM(244580,250849)


def TutorialesCrear():
    return QtGui.QIcon(pmTutorialesCrear())


def pmMover():
    return PM(250849,251431)


def Mover():
    return QtGui.QIcon(pmMover())


def pmSeleccionar():
    return PM(251431,257135)


def Seleccionar():
    return QtGui.QIcon(pmSeleccionar())


def pmVista():
    return PM(257135,259059)


def Vista():
    return QtGui.QIcon(pmVista())


def pmInformacionPGNUno():
    return PM(259059,260437)


def InformacionPGNUno():
    return QtGui.QIcon(pmInformacionPGNUno())


def pmDailyTest():
    return PM(260437,262777)


def DailyTest():
    return QtGui.QIcon(pmDailyTest())


def pmJuegaPorMi():
    return PM(262777,264497)


def JuegaPorMi():
    return QtGui.QIcon(pmJuegaPorMi())


def pmArbol():
    return PM(264497,265131)


def Arbol():
    return QtGui.QIcon(pmArbol())


def pmGrabarFichero():
    return PM(62136,63599)


def GrabarFichero():
    return QtGui.QIcon(pmGrabarFichero())


def pmClipboard():
    return PM(265131,265909)


def Clipboard():
    return QtGui.QIcon(pmClipboard())


def pmFics():
    return PM(265909,266326)


def Fics():
    return QtGui.QIcon(pmFics())


def pmFide():
    return PM(9646,11623)


def Fide():
    return QtGui.QIcon(pmFide())


def pmFichPGN():
    return PM(25146,26894)


def FichPGN():
    return QtGui.QIcon(pmFichPGN())


def pmFlechas():
    return PM(266326,269678)


def Flechas():
    return QtGui.QIcon(pmFlechas())


def pmMarcos():
    return PM(269678,271125)


def Marcos():
    return QtGui.QIcon(pmMarcos())


def pmSVGs():
    return PM(271125,274694)


def SVGs():
    return QtGui.QIcon(pmSVGs())


def pmAmarillo():
    return PM(274694,275946)


def Amarillo():
    return QtGui.QIcon(pmAmarillo())


def pmNaranja():
    return PM(275946,277178)


def Naranja():
    return QtGui.QIcon(pmNaranja())


def pmVerde():
    return PM(277178,278454)


def Verde():
    return QtGui.QIcon(pmVerde())


def pmAzul():
    return PM(278454,279542)


def Azul():
    return QtGui.QIcon(pmAzul())


def pmMagenta():
    return PM(279542,280830)


def Magenta():
    return QtGui.QIcon(pmMagenta())


def pmRojo():
    return PM(280830,282049)


def Rojo():
    return QtGui.QIcon(pmRojo())


def pmGris():
    return PM(282049,283007)


def Gris():
    return QtGui.QIcon(pmGris())


def pmAmarillo32():
    return PM(283007,284987)


def Amarillo32():
    return QtGui.QIcon(pmAmarillo32())


def pmNaranja32():
    return PM(284987,287111)


def Naranja32():
    return QtGui.QIcon(pmNaranja32())


def pmVerde32():
    return PM(287111,289232)


def Verde32():
    return QtGui.QIcon(pmVerde32())


def pmAzul32():
    return PM(289232,291611)


def Azul32():
    return QtGui.QIcon(pmAzul32())


def pmMagenta32():
    return PM(291611,294062)


def Magenta32():
    return QtGui.QIcon(pmMagenta32())


def pmRojo32():
    return PM(294062,295877)


def Rojo32():
    return QtGui.QIcon(pmRojo32())


def pmGris32():
    return PM(295877,297791)


def Gris32():
    return QtGui.QIcon(pmGris32())


def pmPuntoBlanco():
    return PM(297791,298140)


def PuntoBlanco():
    return QtGui.QIcon(pmPuntoBlanco())


def pmPuntoAmarillo():
    return PM(212930,213392)


def PuntoAmarillo():
    return QtGui.QIcon(pmPuntoAmarillo())


def pmPuntoNaranja():
    return PM(298140,298602)


def PuntoNaranja():
    return QtGui.QIcon(pmPuntoNaranja())


def pmPuntoVerde():
    return PM(213715,214177)


def PuntoVerde():
    return QtGui.QIcon(pmPuntoVerde())


def pmPuntoAzul():
    return PM(240387,240849)


def PuntoAzul():
    return QtGui.QIcon(pmPuntoAzul())


def pmPuntoMagenta():
    return PM(298602,299101)


def PuntoMagenta():
    return QtGui.QIcon(pmPuntoMagenta())


def pmPuntoRojo():
    return PM(299101,299600)


def PuntoRojo():
    return QtGui.QIcon(pmPuntoRojo())


def pmPuntoNegro():
    return PM(213392,213715)


def PuntoNegro():
    return QtGui.QIcon(pmPuntoNegro())


def pmPuntoEstrella():
    return PM(299600,300027)


def PuntoEstrella():
    return QtGui.QIcon(pmPuntoEstrella())


def pmComentario():
    return PM(300027,300664)


def Comentario():
    return QtGui.QIcon(pmComentario())


def pmComentarioMas():
    return PM(300664,301603)


def ComentarioMas():
    return QtGui.QIcon(pmComentarioMas())


def pmComentarioEditar():
    return PM(218549,219405)


def ComentarioEditar():
    return QtGui.QIcon(pmComentarioEditar())


def pmOpeningComentario():
    return PM(301603,302599)


def OpeningComentario():
    return QtGui.QIcon(pmOpeningComentario())


def pmMas():
    return PM(302599,303108)


def Mas():
    return QtGui.QIcon(pmMas())


def pmMasR():
    return PM(303108,303596)


def MasR():
    return QtGui.QIcon(pmMasR())


def pmMasDoc():
    return PM(303596,304397)


def MasDoc():
    return QtGui.QIcon(pmMasDoc())


def pmPotencia():
    return PM(178622,179488)


def Potencia():
    return QtGui.QIcon(pmPotencia())


def pmBMT():
    return PM(304397,305275)


def BMT():
    return QtGui.QIcon(pmBMT())


def pmOjo():
    return PM(305275,306397)


def Ojo():
    return QtGui.QIcon(pmOjo())


def pmOcultar():
    return PM(305275,306397)


def Ocultar():
    return QtGui.QIcon(pmOcultar())


def pmMostrar():
    return PM(306397,307453)


def Mostrar():
    return QtGui.QIcon(pmMostrar())


def pmBlog():
    return PM(307453,307975)


def Blog():
    return QtGui.QIcon(pmBlog())


def pmVariations():
    return PM(307975,308882)


def Variations():
    return QtGui.QIcon(pmVariations())


def pmVariationsG():
    return PM(308882,311309)


def VariationsG():
    return QtGui.QIcon(pmVariationsG())


def pmCambiar():
    return PM(311309,313023)


def Cambiar():
    return QtGui.QIcon(pmCambiar())


def pmAnterior():
    return PM(313023,315077)


def Anterior():
    return QtGui.QIcon(pmAnterior())


def pmSiguiente():
    return PM(315077,317147)


def Siguiente():
    return QtGui.QIcon(pmSiguiente())


def pmSiguienteF():
    return PM(317147,319322)


def SiguienteF():
    return QtGui.QIcon(pmSiguienteF())


def pmAnteriorF():
    return PM(319322,321516)


def AnteriorF():
    return QtGui.QIcon(pmAnteriorF())


def pmX():
    return PM(321516,322798)


def X():
    return QtGui.QIcon(pmX())


def pmTools():
    return PM(322798,325399)


def Tools():
    return QtGui.QIcon(pmTools())


def pmTacticas():
    return PM(325399,327972)


def Tacticas():
    return QtGui.QIcon(pmTacticas())


def pmCancelarPeque():
    return PM(327972,328534)


def CancelarPeque():
    return QtGui.QIcon(pmCancelarPeque())


def pmAceptarPeque():
    return PM(214177,215194)


def AceptarPeque():
    return QtGui.QIcon(pmAceptarPeque())


def pmLibre():
    return PM(328534,330926)


def Libre():
    return QtGui.QIcon(pmLibre())


def pmEnBlanco():
    return PM(330926,331652)


def EnBlanco():
    return QtGui.QIcon(pmEnBlanco())


def pmDirector():
    return PM(331652,334626)


def Director():
    return QtGui.QIcon(pmDirector())


def pmTorneos():
    return PM(334626,336364)


def Torneos():
    return QtGui.QIcon(pmTorneos())


def pmOpenings():
    return PM(336364,337289)


def Openings():
    return QtGui.QIcon(pmOpenings())


def pmV_Blancas():
    return PM(337289,337569)


def V_Blancas():
    return QtGui.QIcon(pmV_Blancas())


def pmV_Blancas_Mas():
    return PM(337569,337849)


def V_Blancas_Mas():
    return QtGui.QIcon(pmV_Blancas_Mas())


def pmV_Blancas_Mas_Mas():
    return PM(337849,338121)


def V_Blancas_Mas_Mas():
    return QtGui.QIcon(pmV_Blancas_Mas_Mas())


def pmV_Negras():
    return PM(338121,338396)


def V_Negras():
    return QtGui.QIcon(pmV_Negras())


def pmV_Negras_Mas():
    return PM(338396,338671)


def V_Negras_Mas():
    return QtGui.QIcon(pmV_Negras_Mas())


def pmV_Negras_Mas_Mas():
    return PM(338671,338940)


def V_Negras_Mas_Mas():
    return QtGui.QIcon(pmV_Negras_Mas_Mas())


def pmV_Blancas_Igual_Negras():
    return PM(338940,339242)


def V_Blancas_Igual_Negras():
    return QtGui.QIcon(pmV_Blancas_Igual_Negras())


def pmMezclar():
    return PM(136657,139053)


def Mezclar():
    return QtGui.QIcon(pmMezclar())


def pmVoyager():
    return PM(339242,340085)


def Voyager():
    return QtGui.QIcon(pmVoyager())


def pmVoyager32():
    return PM(340085,341973)


def Voyager32():
    return QtGui.QIcon(pmVoyager32())


def pmReindexar():
    return PM(341973,343790)


def Reindexar():
    return QtGui.QIcon(pmReindexar())


def pmRename():
    return PM(343790,344774)


def Rename():
    return QtGui.QIcon(pmRename())


def pmAdd():
    return PM(344774,345727)


def Add():
    return QtGui.QIcon(pmAdd())


def pmMas22():
    return PM(345727,346391)


def Mas22():
    return QtGui.QIcon(pmMas22())


def pmMenos22():
    return PM(346391,346835)


def Menos22():
    return QtGui.QIcon(pmMenos22())


def pmTransposition():
    return PM(346835,347354)


def Transposition():
    return QtGui.QIcon(pmTransposition())


def pmRat():
    return PM(347354,353058)


def Rat():
    return QtGui.QIcon(pmRat())


def pmAlligator():
    return PM(353058,358050)


def Alligator():
    return QtGui.QIcon(pmAlligator())


def pmAnt():
    return PM(358050,364748)


def Ant():
    return QtGui.QIcon(pmAnt())


def pmBat():
    return PM(364748,367702)


def Bat():
    return QtGui.QIcon(pmBat())


def pmBear():
    return PM(367702,374981)


def Bear():
    return QtGui.QIcon(pmBear())


def pmBee():
    return PM(374981,379983)


def Bee():
    return QtGui.QIcon(pmBee())


def pmBird():
    return PM(379983,386042)


def Bird():
    return QtGui.QIcon(pmBird())


def pmBull():
    return PM(386042,393011)


def Bull():
    return QtGui.QIcon(pmBull())


def pmBulldog():
    return PM(393011,399902)


def Bulldog():
    return QtGui.QIcon(pmBulldog())


def pmButterfly():
    return PM(399902,407276)


def Butterfly():
    return QtGui.QIcon(pmButterfly())


def pmCat():
    return PM(407276,413548)


def Cat():
    return QtGui.QIcon(pmCat())


def pmChicken():
    return PM(413548,419359)


def Chicken():
    return QtGui.QIcon(pmChicken())


def pmCow():
    return PM(419359,426102)


def Cow():
    return QtGui.QIcon(pmCow())


def pmCrab():
    return PM(426102,431691)


def Crab():
    return QtGui.QIcon(pmCrab())


def pmCrocodile():
    return PM(431691,437832)


def Crocodile():
    return QtGui.QIcon(pmCrocodile())


def pmDeer():
    return PM(437832,444139)


def Deer():
    return QtGui.QIcon(pmDeer())


def pmDog():
    return PM(444139,450742)


def Dog():
    return QtGui.QIcon(pmDog())


def pmDonkey():
    return PM(450742,456389)


def Donkey():
    return QtGui.QIcon(pmDonkey())


def pmDuck():
    return PM(456389,462932)


def Duck():
    return QtGui.QIcon(pmDuck())


def pmEagle():
    return PM(462932,467750)


def Eagle():
    return QtGui.QIcon(pmEagle())


def pmElephant():
    return PM(467750,474231)


def Elephant():
    return QtGui.QIcon(pmElephant())


def pmFish():
    return PM(474231,481072)


def Fish():
    return QtGui.QIcon(pmFish())


def pmFox():
    return PM(481072,487855)


def Fox():
    return QtGui.QIcon(pmFox())


def pmFrog():
    return PM(487855,494271)


def Frog():
    return QtGui.QIcon(pmFrog())


def pmGiraffe():
    return PM(494271,501449)


def Giraffe():
    return QtGui.QIcon(pmGiraffe())


def pmGorilla():
    return PM(501449,507988)


def Gorilla():
    return QtGui.QIcon(pmGorilla())


def pmHippo():
    return PM(507988,515109)


def Hippo():
    return QtGui.QIcon(pmHippo())


def pmHorse():
    return PM(515109,521656)


def Horse():
    return QtGui.QIcon(pmHorse())


def pmInsect():
    return PM(521656,527591)


def Insect():
    return QtGui.QIcon(pmInsect())


def pmLion():
    return PM(527591,536501)


def Lion():
    return QtGui.QIcon(pmLion())


def pmMonkey():
    return PM(536501,544180)


def Monkey():
    return QtGui.QIcon(pmMonkey())


def pmMoose():
    return PM(544180,550804)


def Moose():
    return QtGui.QIcon(pmMoose())


def pmMouse():
    return PM(347354,353058)


def Mouse():
    return QtGui.QIcon(pmMouse())


def pmOwl():
    return PM(550804,557510)


def Owl():
    return QtGui.QIcon(pmOwl())


def pmPanda():
    return PM(557510,561544)


def Panda():
    return QtGui.QIcon(pmPanda())


def pmPenguin():
    return PM(561544,567093)


def Penguin():
    return QtGui.QIcon(pmPenguin())


def pmPig():
    return PM(567093,575133)


def Pig():
    return QtGui.QIcon(pmPig())


def pmRabbit():
    return PM(575133,582434)


def Rabbit():
    return QtGui.QIcon(pmRabbit())


def pmRhino():
    return PM(582434,588821)


def Rhino():
    return QtGui.QIcon(pmRhino())


def pmRooster():
    return PM(588821,594084)


def Rooster():
    return QtGui.QIcon(pmRooster())


def pmShark():
    return PM(594084,599854)


def Shark():
    return QtGui.QIcon(pmShark())


def pmSheep():
    return PM(599854,603685)


def Sheep():
    return QtGui.QIcon(pmSheep())


def pmSnake():
    return PM(603685,609710)


def Snake():
    return QtGui.QIcon(pmSnake())


def pmTiger():
    return PM(609710,617747)


def Tiger():
    return QtGui.QIcon(pmTiger())


def pmTurkey():
    return PM(617747,625161)


def Turkey():
    return QtGui.QIcon(pmTurkey())


def pmTurtle():
    return PM(625161,631882)


def Turtle():
    return QtGui.QIcon(pmTurtle())


def pmWolf():
    return PM(631882,634977)


def Wolf():
    return QtGui.QIcon(pmWolf())


def pmSteven():
    return PM(634977,638637)


def Steven():
    return QtGui.QIcon(pmSteven())


def pmKnightMan():
    return PM(638637,645789)


def KnightMan():
    return QtGui.QIcon(pmKnightMan())


def pmWheel():
    return PM(645789,653854)


def Wheel():
    return QtGui.QIcon(pmWheel())


def pmWheelchair():
    return PM(653854,662658)


def Wheelchair():
    return QtGui.QIcon(pmWheelchair())


def pmTouringMotorcycle():
    return PM(662658,668970)


def TouringMotorcycle():
    return QtGui.QIcon(pmTouringMotorcycle())


def pmContainer():
    return PM(668970,674305)


def Container():
    return QtGui.QIcon(pmContainer())


def pmBoatEquipment():
    return PM(674305,679828)


def BoatEquipment():
    return QtGui.QIcon(pmBoatEquipment())


def pmCar():
    return PM(679828,684474)


def Car():
    return QtGui.QIcon(pmCar())


def pmLorry():
    return PM(684474,690510)


def Lorry():
    return QtGui.QIcon(pmLorry())


def pmCarTrailer():
    return PM(690510,694607)


def CarTrailer():
    return QtGui.QIcon(pmCarTrailer())


def pmTowTruck():
    return PM(694607,699365)


def TowTruck():
    return QtGui.QIcon(pmTowTruck())


def pmQuadBike():
    return PM(699365,705334)


def QuadBike():
    return QtGui.QIcon(pmQuadBike())


def pmRecoveryTruck():
    return PM(705334,710331)


def RecoveryTruck():
    return QtGui.QIcon(pmRecoveryTruck())


def pmContainerLoader():
    return PM(710331,715473)


def ContainerLoader():
    return QtGui.QIcon(pmContainerLoader())


def pmPoliceCar():
    return PM(715473,720305)


def PoliceCar():
    return QtGui.QIcon(pmPoliceCar())


def pmExecutiveCar():
    return PM(720305,724983)


def ExecutiveCar():
    return QtGui.QIcon(pmExecutiveCar())


def pmTruck():
    return PM(724983,730446)


def Truck():
    return QtGui.QIcon(pmTruck())


def pmExcavator():
    return PM(730446,735337)


def Excavator():
    return QtGui.QIcon(pmExcavator())


def pmCabriolet():
    return PM(735337,740175)


def Cabriolet():
    return QtGui.QIcon(pmCabriolet())


def pmMixerTruck():
    return PM(740175,746485)


def MixerTruck():
    return QtGui.QIcon(pmMixerTruck())


def pmForkliftTruckLoaded():
    return PM(746485,752633)


def ForkliftTruckLoaded():
    return QtGui.QIcon(pmForkliftTruckLoaded())


def pmAmbulance():
    return PM(752633,758683)


def Ambulance():
    return QtGui.QIcon(pmAmbulance())


def pmDieselLocomotiveBoxcar():
    return PM(758683,762689)


def DieselLocomotiveBoxcar():
    return QtGui.QIcon(pmDieselLocomotiveBoxcar())


def pmTractorUnit():
    return PM(762689,768156)


def TractorUnit():
    return QtGui.QIcon(pmTractorUnit())


def pmFireTruck():
    return PM(768156,774495)


def FireTruck():
    return QtGui.QIcon(pmFireTruck())


def pmCargoShip():
    return PM(774495,778836)


def CargoShip():
    return QtGui.QIcon(pmCargoShip())


def pmSubwayTrain():
    return PM(778836,783726)


def SubwayTrain():
    return QtGui.QIcon(pmSubwayTrain())


def pmTruckMountedCrane():
    return PM(783726,789467)


def TruckMountedCrane():
    return QtGui.QIcon(pmTruckMountedCrane())


def pmAirAmbulance():
    return PM(789467,794580)


def AirAmbulance():
    return QtGui.QIcon(pmAirAmbulance())


def pmAirplane():
    return PM(794580,799468)


def Airplane():
    return QtGui.QIcon(pmAirplane())


def pmCaracol():
    return PM(799468,801284)


def Caracol():
    return QtGui.QIcon(pmCaracol())


def pmUno():
    return PM(801284,803746)


def Uno():
    return QtGui.QIcon(pmUno())


def pmMotoresExternos():
    return PM(803746,805648)


def MotoresExternos():
    return QtGui.QIcon(pmMotoresExternos())


def pmDatabase():
    return PM(805648,806964)


def Database():
    return QtGui.QIcon(pmDatabase())


def pmDatabaseMas():
    return PM(806964,808423)


def DatabaseMas():
    return QtGui.QIcon(pmDatabaseMas())


def pmDatabaseImport():
    return PM(808423,809059)


def DatabaseImport():
    return QtGui.QIcon(pmDatabaseImport())


def pmDatabaseExport():
    return PM(809059,809704)


def DatabaseExport():
    return QtGui.QIcon(pmDatabaseExport())


def pmDatabaseDelete():
    return PM(809704,810827)


def DatabaseDelete():
    return QtGui.QIcon(pmDatabaseDelete())


def pmDatabaseMaintenance():
    return PM(810827,812323)


def DatabaseMaintenance():
    return QtGui.QIcon(pmDatabaseMaintenance())


def pmAtacante():
    return PM(812323,812928)


def Atacante():
    return QtGui.QIcon(pmAtacante())


def pmAtacada():
    return PM(812928,813494)


def Atacada():
    return QtGui.QIcon(pmAtacada())


def pmGoToNext():
    return PM(813494,813906)


def GoToNext():
    return QtGui.QIcon(pmGoToNext())


def pmBlancas():
    return PM(813906,814257)


def Blancas():
    return QtGui.QIcon(pmBlancas())


def pmNegras():
    return PM(814257,814503)


def Negras():
    return QtGui.QIcon(pmNegras())


def pmFolderChange():
    return PM(65651,68409)


def FolderChange():
    return QtGui.QIcon(pmFolderChange())


def pmMarkers():
    return PM(814503,816198)


def Markers():
    return QtGui.QIcon(pmMarkers())


def pmTop():
    return PM(816198,816782)


def Top():
    return QtGui.QIcon(pmTop())


def pmBottom():
    return PM(816782,817371)


def Bottom():
    return QtGui.QIcon(pmBottom())


def pmSTS():
    return PM(817371,819562)


def STS():
    return QtGui.QIcon(pmSTS())


def pmRun():
    return PM(819562,821286)


def Run():
    return QtGui.QIcon(pmRun())


def pmRun2():
    return PM(821286,822806)


def Run2():
    return QtGui.QIcon(pmRun2())


def pmWorldMap():
    return PM(822806,825547)


def WorldMap():
    return QtGui.QIcon(pmWorldMap())


def pmAfrica():
    return PM(825547,828033)


def Africa():
    return QtGui.QIcon(pmAfrica())


def pmMaps():
    return PM(828033,828977)


def Maps():
    return QtGui.QIcon(pmMaps())


def pmSol():
    return PM(828977,829903)


def Sol():
    return QtGui.QIcon(pmSol())


def pmSolNubes():
    return PM(829903,830766)


def SolNubes():
    return QtGui.QIcon(pmSolNubes())


def pmSolNubesLluvia():
    return PM(830766,831726)


def SolNubesLluvia():
    return QtGui.QIcon(pmSolNubesLluvia())


def pmLluvia():
    return PM(831726,832565)


def Lluvia():
    return QtGui.QIcon(pmLluvia())


def pmInvierno():
    return PM(832565,834141)


def Invierno():
    return QtGui.QIcon(pmInvierno())


def pmFixedElo():
    return PM(158968,160231)


def FixedElo():
    return QtGui.QIcon(pmFixedElo())


def pmSoundTool():
    return PM(834141,836600)


def SoundTool():
    return QtGui.QIcon(pmSoundTool())


def pmTrain():
    return PM(836600,837970)


def Train():
    return QtGui.QIcon(pmTrain())


def pmPlay():
    return PM(225173,227262)


def Play():
    return QtGui.QIcon(pmPlay())


def pmMeasure():
    return PM(120753,122376)


def Measure():
    return QtGui.QIcon(pmMeasure())


def pmPlayGame():
    return PM(837970,842328)


def PlayGame():
    return QtGui.QIcon(pmPlayGame())


def pmScanner():
    return PM(842328,842669)


def Scanner():
    return QtGui.QIcon(pmScanner())


def pmCursorScanner():
    return PM(842669,842986)


def CursorScanner():
    return QtGui.QIcon(pmCursorScanner())


def pmMenos():
    return PM(842986,843511)


def Menos():
    return QtGui.QIcon(pmMenos())


def pmSchool():
    return PM(843511,844873)


def School():
    return QtGui.QIcon(pmSchool())


def pmLaw():
    return PM(844873,845489)


def Law():
    return QtGui.QIcon(pmLaw())


def pmLearnGame():
    return PM(845489,845922)


def LearnGame():
    return QtGui.QIcon(pmLearnGame())


def pmLonghaul():
    return PM(845922,846848)


def Longhaul():
    return QtGui.QIcon(pmLonghaul())


def pmTrekking():
    return PM(846848,847542)


def Trekking():
    return QtGui.QIcon(pmTrekking())


def pmPassword():
    return PM(847542,847995)


def Password():
    return QtGui.QIcon(pmPassword())


def pmSQL_RAW():
    return PM(837970,842328)


def SQL_RAW():
    return QtGui.QIcon(pmSQL_RAW())


def pmSun():
    return PM(304397,305275)


def Sun():
    return QtGui.QIcon(pmSun())


def pmLight32():
    return PM(847995,849695)


def Light32():
    return QtGui.QIcon(pmLight32())


def pmTOL():
    return PM(849695,850404)


def TOL():
    return QtGui.QIcon(pmTOL())


def pmUned():
    return PM(850404,850824)


def Uned():
    return QtGui.QIcon(pmUned())


def pmUwe():
    return PM(850824,851793)


def Uwe():
    return QtGui.QIcon(pmUwe())


def pmThinking():
    return PM(851793,852582)


def Thinking():
    return QtGui.QIcon(pmThinking())


def pmWashingMachine():
    return PM(852582,853245)


def WashingMachine():
    return QtGui.QIcon(pmWashingMachine())


def pmTerminal():
    return PM(853245,856789)


def Terminal():
    return QtGui.QIcon(pmTerminal())


def pmManualSave():
    return PM(856789,857372)


def ManualSave():
    return QtGui.QIcon(pmManualSave())


def pmSettings():
    return PM(857372,857810)


def Settings():
    return QtGui.QIcon(pmSettings())


def pmStrength():
    return PM(857810,858481)


def Strength():
    return QtGui.QIcon(pmStrength())


def pmSingular():
    return PM(858481,859336)


def Singular():
    return QtGui.QIcon(pmSingular())


def pmScript():
    return PM(859336,859905)


def Script():
    return QtGui.QIcon(pmScript())


def pmTexto():
    return PM(859905,862750)


def Texto():
    return QtGui.QIcon(pmTexto())


def pmLampara():
    return PM(862750,863459)


def Lampara():
    return QtGui.QIcon(pmLampara())


def pmFile():
    return PM(863459,865759)


def File():
    return QtGui.QIcon(pmFile())


def pmCalculo():
    return PM(865759,866685)


def Calculo():
    return QtGui.QIcon(pmCalculo())


def pmOpeningLines():
    return PM(866685,867363)


def OpeningLines():
    return QtGui.QIcon(pmOpeningLines())


def pmStudy():
    return PM(867363,868276)


def Study():
    return QtGui.QIcon(pmStudy())


def pmLichess():
    return PM(868276,869164)


def Lichess():
    return QtGui.QIcon(pmLichess())


def pmMiniatura():
    return PM(869164,870091)


def Miniatura():
    return QtGui.QIcon(pmMiniatura())


def pmLocomotora():
    return PM(870091,870872)


def Locomotora():
    return QtGui.QIcon(pmLocomotora())


def pmTrainSequential():
    return PM(870872,872013)


def TrainSequential():
    return QtGui.QIcon(pmTrainSequential())


def pmTrainStatic():
    return PM(872013,872973)


def TrainStatic():
    return QtGui.QIcon(pmTrainStatic())


def pmTrainPositions():
    return PM(872973,873954)


def TrainPositions():
    return QtGui.QIcon(pmTrainPositions())


def pmTrainEngines():
    return PM(873954,875388)


def TrainEngines():
    return QtGui.QIcon(pmTrainEngines())


def pmError():
    return PM(41940,45940)


def Error():
    return QtGui.QIcon(pmError())


def pmAtajos():
    return PM(875388,876567)


def Atajos():
    return QtGui.QIcon(pmAtajos())


def pmTOLline():
    return PM(876567,877671)


def TOLline():
    return QtGui.QIcon(pmTOLline())


def pmTOLchange():
    return PM(877671,879893)


def TOLchange():
    return QtGui.QIcon(pmTOLchange())


def pmPack():
    return PM(879893,881066)


def Pack():
    return QtGui.QIcon(pmPack())


def pmHome():
    return PM(173978,175160)


def Home():
    return QtGui.QIcon(pmHome())


def pmImport8():
    return PM(881066,881988)


def Import8():
    return QtGui.QIcon(pmImport8())


def pmExport8():
    return PM(881988,882888)


def Export8():
    return QtGui.QIcon(pmExport8())


def pmTablas8():
    return PM(882888,883680)


def Tablas8():
    return QtGui.QIcon(pmTablas8())


def pmBlancas8():
    return PM(883680,884710)


def Blancas8():
    return QtGui.QIcon(pmBlancas8())


def pmNegras8():
    return PM(884710,885549)


def Negras8():
    return QtGui.QIcon(pmNegras8())


def pmBook():
    return PM(885549,886123)


def Book():
    return QtGui.QIcon(pmBook())


def pmWrite():
    return PM(886123,887328)


def Write():
    return QtGui.QIcon(pmWrite())


def pmAlt():
    return PM(887328,887770)


def Alt():
    return QtGui.QIcon(pmAlt())


def pmShift():
    return PM(887770,888110)


def Shift():
    return QtGui.QIcon(pmShift())


def pmRightMouse():
    return PM(888110,888910)


def RightMouse():
    return QtGui.QIcon(pmRightMouse())


def pmControl():
    return PM(888910,889435)


def Control():
    return QtGui.QIcon(pmControl())


def pmFinales():
    return PM(889435,890522)


def Finales():
    return QtGui.QIcon(pmFinales())


def pmEditColumns():
    return PM(890522,891254)


def EditColumns():
    return QtGui.QIcon(pmEditColumns())


def pmResizeAll():
    return PM(891254,891764)


def ResizeAll():
    return QtGui.QIcon(pmResizeAll())


def pmChecked():
    return PM(891764,892270)


def Checked():
    return QtGui.QIcon(pmChecked())


def pmUnchecked():
    return PM(892270,892518)


def Unchecked():
    return QtGui.QIcon(pmUnchecked())


def pmBuscarC():
    return PM(892518,892962)


def BuscarC():
    return QtGui.QIcon(pmBuscarC())


def pmPeonBlanco():
    return PM(892962,895143)


def PeonBlanco():
    return QtGui.QIcon(pmPeonBlanco())


def pmPeonNegro():
    return PM(895143,896667)


def PeonNegro():
    return QtGui.QIcon(pmPeonNegro())


def pmReciclar():
    return PM(896667,897391)


def Reciclar():
    return QtGui.QIcon(pmReciclar())


def pmLanzamiento():
    return PM(897391,898104)


def Lanzamiento():
    return QtGui.QIcon(pmLanzamiento())


def pmLanzamientos():
    return PM(898104,898698)


def Lanzamientos():
    return QtGui.QIcon(pmLanzamientos())


def pmEndGame():
    return PM(898698,899112)


def EndGame():
    return QtGui.QIcon(pmEndGame())


def pmPause():
    return PM(899112,899981)


def Pause():
    return QtGui.QIcon(pmPause())


def pmContinue():
    return PM(899981,901185)


def Continue():
    return QtGui.QIcon(pmContinue())


def pmClose():
    return PM(901185,901884)


def Close():
    return QtGui.QIcon(pmClose())


def pmStop():
    return PM(901884,902917)


def Stop():
    return QtGui.QIcon(pmStop())


def pmFactoryPolyglot():
    return PM(902917,903737)


def FactoryPolyglot():
    return QtGui.QIcon(pmFactoryPolyglot())


def pmTags():
    return PM(903737,904560)


def Tags():
    return QtGui.QIcon(pmTags())


def pmAppearance():
    return PM(904560,905287)


def Appearance():
    return QtGui.QIcon(pmAppearance())


def pmFill():
    return PM(905287,906325)


def Fill():
    return QtGui.QIcon(pmFill())


def pmSupport():
    return PM(906325,907057)


def Support():
    return QtGui.QIcon(pmSupport())


def pmOrder():
    return PM(907057,907855)


def Order():
    return QtGui.QIcon(pmOrder())


def pmPlay1():
    return PM(907855,909150)


def Play1():
    return QtGui.QIcon(pmPlay1())


def pmRemove1():
    return PM(909150,910277)


def Remove1():
    return QtGui.QIcon(pmRemove1())


def pmNew1():
    return PM(910277,910599)


def New1():
    return QtGui.QIcon(pmNew1())


def pmMensError():
    return PM(910599,912663)


def MensError():
    return QtGui.QIcon(pmMensError())


def pmMensInfo():
    return PM(912663,915218)


def MensInfo():
    return QtGui.QIcon(pmMensInfo())


def pmJump():
    return PM(915218,915893)


def Jump():
    return QtGui.QIcon(pmJump())


def pmCaptures():
    return PM(915893,917074)


def Captures():
    return QtGui.QIcon(pmCaptures())


def pmRepeat():
    return PM(917074,917733)


def Repeat():
    return QtGui.QIcon(pmRepeat())


def pmCount():
    return PM(917733,918409)


def Count():
    return QtGui.QIcon(pmCount())


def pmMate15():
    return PM(918409,919480)


def Mate15():
    return QtGui.QIcon(pmMate15())


def pmCoordinates():
    return PM(919480,920633)


def Coordinates():
    return QtGui.QIcon(pmCoordinates())


def pmKnight():
    return PM(920633,921876)


def Knight():
    return QtGui.QIcon(pmKnight())


def pmCorrecto():
    return PM(921876,922902)


def Correcto():
    return QtGui.QIcon(pmCorrecto())


def pmBlocks():
    return PM(922902,923239)


def Blocks():
    return QtGui.QIcon(pmBlocks())


def pmWest():
    return PM(923239,924345)


def West():
    return QtGui.QIcon(pmWest())


def pmOpening():
    return PM(924345,924603)


def Opening():
    return QtGui.QIcon(pmOpening())


def pmVariation():
    return PM(216513,216931)


def Variation():
    return QtGui.QIcon(pmVariation())


def pmComment():
    return PM(924603,924966)


def Comment():
    return QtGui.QIcon(pmComment())


def pmComment32():
    return PM(924966,925933)


def Comment32():
    return QtGui.QIcon(pmComment32())


def pmVariationComment():
    return PM(925933,926277)


def VariationComment():
    return QtGui.QIcon(pmVariationComment())


def pmOpeningVariation():
    return PM(926277,926741)


def OpeningVariation():
    return QtGui.QIcon(pmOpeningVariation())


def pmOpeningComment():
    return PM(926741,927074)


def OpeningComment():
    return QtGui.QIcon(pmOpeningComment())


def pmOpeningVariationComment():
    return PM(926277,926741)


def OpeningVariationComment():
    return QtGui.QIcon(pmOpeningVariationComment())


def pmDeleteRow():
    return PM(927074,927505)


def DeleteRow():
    return QtGui.QIcon(pmDeleteRow())


def pmDeleteColumn():
    return PM(927505,927948)


def DeleteColumn():
    return QtGui.QIcon(pmDeleteColumn())


def pmEditVariation():
    return PM(927948,928303)


def EditVariation():
    return QtGui.QIcon(pmEditVariation())


def pmKibitzer():
    return PM(928303,928902)


def Kibitzer():
    return QtGui.QIcon(pmKibitzer())


def pmKibitzer_Pause():
    return PM(928902,929074)


def Kibitzer_Pause():
    return QtGui.QIcon(pmKibitzer_Pause())


def pmKibitzer_Options():
    return PM(929074,929976)


def Kibitzer_Options():
    return QtGui.QIcon(pmKibitzer_Options())


def pmKibitzer_Voyager():
    return PM(339242,340085)


def Kibitzer_Voyager():
    return QtGui.QIcon(pmKibitzer_Voyager())


def pmKibitzer_Close():
    return PM(929976,930533)


def Kibitzer_Close():
    return QtGui.QIcon(pmKibitzer_Close())


def pmKibitzer_Down():
    return PM(930533,930922)


def Kibitzer_Down():
    return QtGui.QIcon(pmKibitzer_Down())


def pmKibitzer_Up():
    return PM(930922,931317)


def Kibitzer_Up():
    return QtGui.QIcon(pmKibitzer_Up())


def pmKibitzer_Back():
    return PM(931317,931750)


def Kibitzer_Back():
    return QtGui.QIcon(pmKibitzer_Back())


def pmKibitzer_Clipboard():
    return PM(931750,932136)


def Kibitzer_Clipboard():
    return QtGui.QIcon(pmKibitzer_Clipboard())


def pmKibitzer_Play():
    return PM(932136,932657)


def Kibitzer_Play():
    return QtGui.QIcon(pmKibitzer_Play())


def pmKibitzer_Side():
    return PM(932657,933410)


def Kibitzer_Side():
    return QtGui.QIcon(pmKibitzer_Side())


def pmKibitzer_Board():
    return PM(933410,933848)


def Kibitzer_Board():
    return QtGui.QIcon(pmKibitzer_Board())


def pmBoard():
    return PM(933848,934317)


def Board():
    return QtGui.QIcon(pmBoard())


def pmTraining_Games():
    return PM(934317,936009)


def Training_Games():
    return QtGui.QIcon(pmTraining_Games())


def pmTraining_Basic():
    return PM(936009,937382)


def Training_Basic():
    return QtGui.QIcon(pmTraining_Basic())


def pmTraining_Tactics():
    return PM(937382,938163)


def Training_Tactics():
    return QtGui.QIcon(pmTraining_Tactics())


def pmTraining_Endings():
    return PM(938163,939097)


def Training_Endings():
    return QtGui.QIcon(pmTraining_Endings())


def pmBridge():
    return PM(939097,940115)


def Bridge():
    return QtGui.QIcon(pmBridge())


def pmMaia():
    return PM(940115,940899)


def Maia():
    return QtGui.QIcon(pmMaia())


def pmBinBook():
    return PM(940899,941648)


def BinBook():
    return QtGui.QIcon(pmBinBook())


def pmConnected():
    return PM(941648,941877)


def Connected():
    return QtGui.QIcon(pmConnected())


def pmThemes():
    return PM(941877,942446)


def Themes():
    return QtGui.QIcon(pmThemes())


def pmReset():
    return PM(942446,944065)


def Reset():
    return QtGui.QIcon(pmReset())


def pmInstall():
    return PM(944065,946194)


def Install():
    return QtGui.QIcon(pmInstall())


def pmUninstall():
    return PM(946194,948220)


def Uninstall():
    return QtGui.QIcon(pmUninstall())


def pmLive():
    return PM(948220,951703)


def Live():
    return QtGui.QIcon(pmLive())


def pmLauncher():
    return PM(951703,956378)


def Launcher():
    return QtGui.QIcon(pmLauncher())


def pmLogInactive():
    return PM(956378,956909)


def LogInactive():
    return QtGui.QIcon(pmLogInactive())


def pmLogActive():
    return PM(956909,957473)


def LogActive():
    return QtGui.QIcon(pmLogActive())


def pmFolderAnil():
    return PM(957473,957837)


def FolderAnil():
    return QtGui.QIcon(pmFolderAnil())


def pmFolderBlack():
    return PM(957837,958174)


def FolderBlack():
    return QtGui.QIcon(pmFolderBlack())


def pmFolderBlue():
    return PM(958174,958548)


def FolderBlue():
    return QtGui.QIcon(pmFolderBlue())


def pmFolderGreen():
    return PM(958548,958920)


def FolderGreen():
    return QtGui.QIcon(pmFolderGreen())


def pmFolderMagenta():
    return PM(958920,959293)


def FolderMagenta():
    return QtGui.QIcon(pmFolderMagenta())


def pmFolderRed():
    return PM(959293,959657)


def FolderRed():
    return QtGui.QIcon(pmFolderRed())


def pmThis():
    return PM(959657,960111)


def This():
    return QtGui.QIcon(pmThis())


def pmAll():
    return PM(960111,960614)


def All():
    return QtGui.QIcon(pmAll())


def pmPrevious():
    return PM(960614,961073)


def Previous():
    return QtGui.QIcon(pmPrevious())


def pmLine():
    return PM(961073,961260)


def Line():
    return QtGui.QIcon(pmLine())


def pmEmpty():
    return PM(961260,961345)


def Empty():
    return QtGui.QIcon(pmEmpty())


def pmMore():
    return PM(961345,961634)


def More():
    return QtGui.QIcon(pmMore())


def pmSelectLogo():
    return PM(961634,962240)


def SelectLogo():
    return QtGui.QIcon(pmSelectLogo())


def pmSelect():
    return PM(962240,962894)


def Select():
    return QtGui.QIcon(pmSelect())


def pmSelectClose():
    return PM(962894,963666)


def SelectClose():
    return QtGui.QIcon(pmSelectClose())


def pmSelectHome():
    return PM(963666,964448)


def SelectHome():
    return QtGui.QIcon(pmSelectHome())


def pmSelectHistory():
    return PM(964448,965000)


def SelectHistory():
    return QtGui.QIcon(pmSelectHistory())


def pmSelectExplorer():
    return PM(965000,965733)


def SelectExplorer():
    return QtGui.QIcon(pmSelectExplorer())


def pmSelectFolderCreate():
    return PM(965733,966652)


def SelectFolderCreate():
    return QtGui.QIcon(pmSelectFolderCreate())


def pmSelectFolderRemove():
    return PM(966652,967679)


def SelectFolderRemove():
    return QtGui.QIcon(pmSelectFolderRemove())


def pmSelectReload():
    return PM(967679,969333)


def SelectReload():
    return QtGui.QIcon(pmSelectReload())


def pmSelectAccept():
    return PM(969333,970134)


def SelectAccept():
    return QtGui.QIcon(pmSelectAccept())


def pmWiki():
    return PM(970134,971251)


def Wiki():
    return QtGui.QIcon(pmWiki())


def pmCircle():
    return PM(971251,972711)


def Circle():
    return QtGui.QIcon(pmCircle())


def pmSortAZ():
    return PM(972711,973475)


def SortAZ():
    return QtGui.QIcon(pmSortAZ())


def pmReference():
    return PM(973475,974586)


def Reference():
    return QtGui.QIcon(pmReference())


def pmLanguageNew():
    return PM(974586,975313)


def LanguageNew():
    return QtGui.QIcon(pmLanguageNew())


def pmODT():
    return PM(975313,976428)


def ODT():
    return QtGui.QIcon(pmODT())


def pmEngines():
    return PM(976428,977914)


def Engines():
    return QtGui.QIcon(pmEngines())


def pmConfEngines():
    return PM(977914,979110)


def ConfEngines():
    return QtGui.QIcon(pmConfEngines())


def pmEngine():
    return PM(979110,980534)


def Engine():
    return QtGui.QIcon(pmEngine())


def pmZip():
    return PM(980534,981430)


def Zip():
    return QtGui.QIcon(pmZip())


def pmUpdate():
    return PM(981430,982514)


def Update():
    return QtGui.QIcon(pmUpdate())


def pmDGT():
    return PM(982514,983508)


def DGT():
    return QtGui.QIcon(pmDGT())


def pmDGTB():
    return PM(983508,984210)


def DGTB():
    return QtGui.QIcon(pmDGTB())


def pmMillenium():
    return PM(984210,985447)


def Millenium():
    return QtGui.QIcon(pmMillenium())


def pmCertabo():
    return PM(985447,986232)


def Certabo():
    return QtGui.QIcon(pmCertabo())


def pmNovag():
    return PM(986232,987099)


def Novag():
    return QtGui.QIcon(pmNovag())


def pmChessnut():
    return PM(987099,987874)


def Chessnut():
    return QtGui.QIcon(pmChessnut())


def pmSquareOff():
    return PM(987874,988630)


def SquareOff():
    return QtGui.QIcon(pmSquareOff())


def pmRodent():
    return PM(988630,989748)


def Rodent():
    return QtGui.QIcon(pmRodent())


def pmLeague():
    return PM(989748,991078)


def League():
    return QtGui.QIcon(pmLeague())


def pmJourney():
    return PM(991078,992317)


def Journey():
    return QtGui.QIcon(pmJourney())


def pmClassification():
    return PM(992317,992836)


def Classification():
    return QtGui.QIcon(pmClassification())


def pmNAGs():
    return PM(992836,993133)


def NAGs():
    return QtGui.QIcon(pmNAGs())


def pmSeason():
    return PM(993133,993931)


def Season():
    return QtGui.QIcon(pmSeason())


def pmNAG_0():
    return PM(993931,994152)


def NAG_0():
    return QtGui.QIcon(pmNAG_0())


def pmNAG_1():
    return PM(994152,994587)


def NAG_1():
    return QtGui.QIcon(pmNAG_1())


def pmNAG_2():
    return PM(994587,995144)


def NAG_2():
    return QtGui.QIcon(pmNAG_2())


def pmNAG_3():
    return PM(995144,995930)


def NAG_3():
    return QtGui.QIcon(pmNAG_3())


def pmNAG_4():
    return PM(995930,996741)


def NAG_4():
    return QtGui.QIcon(pmNAG_4())


def pmNAG_5():
    return PM(996741,997602)


def NAG_5():
    return QtGui.QIcon(pmNAG_5())


def pmNAG_6():
    return PM(997602,998382)


def NAG_6():
    return QtGui.QIcon(pmNAG_6())


def pmInformation():
    return PM(998382,1001862)


def Information():
    return QtGui.QIcon(pmInformation())


