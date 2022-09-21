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


def pmMainMenu():
    return PM(54055,58365)


def MainMenu():
    return QtGui.QIcon(pmMainMenu())


def pmFinPartida():
    return PM(58365,61313)


def FinPartida():
    return QtGui.QIcon(pmFinPartida())


def pmGrabar():
    return PM(61313,62776)


def Grabar():
    return QtGui.QIcon(pmGrabar())


def pmGrabarComo():
    return PM(62776,64828)


def GrabarComo():
    return QtGui.QIcon(pmGrabarComo())


def pmRecuperar():
    return PM(64828,67586)


def Recuperar():
    return QtGui.QIcon(pmRecuperar())


def pmInformacion():
    return PM(67586,69545)


def Informacion():
    return QtGui.QIcon(pmInformacion())


def pmNuevo():
    return PM(69545,70299)


def Nuevo():
    return QtGui.QIcon(pmNuevo())


def pmCopiar():
    return PM(70299,71480)


def Copiar():
    return QtGui.QIcon(pmCopiar())


def pmModificar():
    return PM(71480,75877)


def Modificar():
    return QtGui.QIcon(pmModificar())


def pmBorrar():
    return PM(75877,80868)


def Borrar():
    return QtGui.QIcon(pmBorrar())


def pmMarcar():
    return PM(80868,85797)


def Marcar():
    return QtGui.QIcon(pmMarcar())


def pmPegar():
    return PM(85797,88108)


def Pegar():
    return QtGui.QIcon(pmPegar())


def pmFichero():
    return PM(88108,92793)


def Fichero():
    return QtGui.QIcon(pmFichero())


def pmNuestroFichero():
    return PM(92793,95840)


def NuestroFichero():
    return QtGui.QIcon(pmNuestroFichero())


def pmFicheroRepite():
    return PM(95840,97336)


def FicheroRepite():
    return QtGui.QIcon(pmFicheroRepite())


def pmInformacionPGN():
    return PM(97336,98354)


def InformacionPGN():
    return QtGui.QIcon(pmInformacionPGN())


def pmVer():
    return PM(98354,99808)


def Ver():
    return QtGui.QIcon(pmVer())


def pmInicio():
    return PM(99808,101822)


def Inicio():
    return QtGui.QIcon(pmInicio())


def pmFinal():
    return PM(101822,103816)


def Final():
    return QtGui.QIcon(pmFinal())


def pmFiltrar():
    return PM(103816,110306)


def Filtrar():
    return QtGui.QIcon(pmFiltrar())


def pmArriba():
    return PM(110306,112459)


def Arriba():
    return QtGui.QIcon(pmArriba())


def pmAbajo():
    return PM(112459,114567)


def Abajo():
    return QtGui.QIcon(pmAbajo())


def pmEstadisticas():
    return PM(114567,116706)


def Estadisticas():
    return QtGui.QIcon(pmEstadisticas())


def pmCheck():
    return PM(116706,119930)


def Check():
    return QtGui.QIcon(pmCheck())


def pmTablas():
    return PM(119930,121553)


def Tablas():
    return QtGui.QIcon(pmTablas())


def pmAtras():
    return PM(121553,123072)


def Atras():
    return QtGui.QIcon(pmAtras())


def pmBuscar():
    return PM(123072,125057)


def Buscar():
    return QtGui.QIcon(pmBuscar())


def pmLibros():
    return PM(125057,127185)


def Libros():
    return QtGui.QIcon(pmLibros())


def pmAceptar():
    return PM(127185,130532)


def Aceptar():
    return QtGui.QIcon(pmAceptar())


def pmCancelar():
    return PM(130532,132515)


def Cancelar():
    return QtGui.QIcon(pmCancelar())


def pmDefecto():
    return PM(132515,135834)


def Defecto():
    return QtGui.QIcon(pmDefecto())


def pmInsertar():
    return PM(135834,138230)


def Insertar():
    return QtGui.QIcon(pmInsertar())


def pmJugar():
    return PM(138230,140439)


def Jugar():
    return QtGui.QIcon(pmJugar())


def pmConfigurar():
    return PM(140439,143523)


def Configurar():
    return QtGui.QIcon(pmConfigurar())


def pmS_Aceptar():
    return PM(127185,130532)


def S_Aceptar():
    return QtGui.QIcon(pmS_Aceptar())


def pmS_Cancelar():
    return PM(130532,132515)


def S_Cancelar():
    return QtGui.QIcon(pmS_Cancelar())


def pmS_Microfono():
    return PM(143523,148964)


def S_Microfono():
    return QtGui.QIcon(pmS_Microfono())


def pmS_LeerWav():
    return PM(39340,41940)


def S_LeerWav():
    return QtGui.QIcon(pmS_LeerWav())


def pmS_Play():
    return PM(148964,154302)


def S_Play():
    return QtGui.QIcon(pmS_Play())


def pmS_StopPlay():
    return PM(154302,154912)


def S_StopPlay():
    return QtGui.QIcon(pmS_StopPlay())


def pmS_StopMicrofono():
    return PM(154302,154912)


def S_StopMicrofono():
    return QtGui.QIcon(pmS_StopMicrofono())


def pmS_Record():
    return PM(154912,158145)


def S_Record():
    return QtGui.QIcon(pmS_Record())


def pmS_Limpiar():
    return PM(75877,80868)


def S_Limpiar():
    return QtGui.QIcon(pmS_Limpiar())


def pmHistorial():
    return PM(158145,159408)


def Historial():
    return QtGui.QIcon(pmHistorial())


def pmPegar16():
    return PM(159408,160402)


def Pegar16():
    return QtGui.QIcon(pmPegar16())


def pmRivalesMP():
    return PM(160402,163084)


def RivalesMP():
    return QtGui.QIcon(pmRivalesMP())


def pmCamara():
    return PM(163084,164606)


def Camara():
    return QtGui.QIcon(pmCamara())


def pmUsuarios():
    return PM(164606,165846)


def Usuarios():
    return QtGui.QIcon(pmUsuarios())


def pmResistencia():
    return PM(165846,168908)


def Resistencia():
    return QtGui.QIcon(pmResistencia())


def pmCebra():
    return PM(168908,171361)


def Cebra():
    return QtGui.QIcon(pmCebra())


def pmGafas():
    return PM(171361,172519)


def Gafas():
    return QtGui.QIcon(pmGafas())


def pmPuente():
    return PM(172519,173155)


def Puente():
    return QtGui.QIcon(pmPuente())


def pmWeb():
    return PM(173155,174337)


def Web():
    return QtGui.QIcon(pmWeb())


def pmMail():
    return PM(174337,175297)


def Mail():
    return QtGui.QIcon(pmMail())


def pmAyuda():
    return PM(175297,176478)


def Ayuda():
    return QtGui.QIcon(pmAyuda())


def pmFAQ():
    return PM(176478,177799)


def FAQ():
    return QtGui.QIcon(pmFAQ())


def pmActualiza():
    return PM(177799,178665)


def Actualiza():
    return QtGui.QIcon(pmActualiza())


def pmRefresh():
    return PM(178665,181057)


def Refresh():
    return QtGui.QIcon(pmRefresh())


def pmJuegaSolo():
    return PM(181057,182909)


def JuegaSolo():
    return QtGui.QIcon(pmJuegaSolo())


def pmPlayer():
    return PM(182909,184091)


def Player():
    return QtGui.QIcon(pmPlayer())


def pmJS_Rotacion():
    return PM(184091,186001)


def JS_Rotacion():
    return QtGui.QIcon(pmJS_Rotacion())


def pmElo():
    return PM(186001,187507)


def Elo():
    return QtGui.QIcon(pmElo())


def pmMate():
    return PM(187507,188068)


def Mate():
    return QtGui.QIcon(pmMate())


def pmEloTimed():
    return PM(188068,189552)


def EloTimed():
    return QtGui.QIcon(pmEloTimed())


def pmPGN():
    return PM(189552,191550)


def PGN():
    return QtGui.QIcon(pmPGN())


def pmPGN_Importar():
    return PM(191550,193140)


def PGN_Importar():
    return QtGui.QIcon(pmPGN_Importar())


def pmAyudaGR():
    return PM(193140,199018)


def AyudaGR():
    return QtGui.QIcon(pmAyudaGR())


def pmBotonAyuda():
    return PM(199018,201478)


def BotonAyuda():
    return QtGui.QIcon(pmBotonAyuda())


def pmColores():
    return PM(201478,202709)


def Colores():
    return QtGui.QIcon(pmColores())


def pmEditarColores():
    return PM(202709,205012)


def EditarColores():
    return QtGui.QIcon(pmEditarColores())


def pmGranMaestro():
    return PM(205012,205868)


def GranMaestro():
    return QtGui.QIcon(pmGranMaestro())


def pmFavoritos():
    return PM(205868,207634)


def Favoritos():
    return QtGui.QIcon(pmFavoritos())


def pmCarpeta():
    return PM(207634,208338)


def Carpeta():
    return QtGui.QIcon(pmCarpeta())


def pmDivision():
    return PM(208338,209003)


def Division():
    return QtGui.QIcon(pmDivision())


def pmDivisionF():
    return PM(209003,210117)


def DivisionF():
    return QtGui.QIcon(pmDivisionF())


def pmDelete():
    return PM(210117,211041)


def Delete():
    return QtGui.QIcon(pmDelete())


def pmModificarP():
    return PM(211041,212107)


def ModificarP():
    return QtGui.QIcon(pmModificarP())


def pmGrupo_Si():
    return PM(212107,212569)


def Grupo_Si():
    return QtGui.QIcon(pmGrupo_Si())


def pmGrupo_No():
    return PM(212569,212892)


def Grupo_No():
    return QtGui.QIcon(pmGrupo_No())


def pmMotor_Si():
    return PM(212892,213354)


def Motor_Si():
    return QtGui.QIcon(pmMotor_Si())


def pmMotor_No():
    return PM(210117,211041)


def Motor_No():
    return QtGui.QIcon(pmMotor_No())


def pmMotor_Actual():
    return PM(213354,214371)


def Motor_Actual():
    return QtGui.QIcon(pmMotor_Actual())


def pmMoverInicio():
    return PM(214371,214669)


def MoverInicio():
    return QtGui.QIcon(pmMoverInicio())


def pmMoverFinal():
    return PM(214669,214970)


def MoverFinal():
    return QtGui.QIcon(pmMoverFinal())


def pmMoverAdelante():
    return PM(214970,215325)


def MoverAdelante():
    return QtGui.QIcon(pmMoverAdelante())


def pmMoverAtras():
    return PM(215325,215690)


def MoverAtras():
    return QtGui.QIcon(pmMoverAtras())


def pmMoverLibre():
    return PM(215690,216108)


def MoverLibre():
    return QtGui.QIcon(pmMoverLibre())


def pmMoverTiempo():
    return PM(216108,216687)


def MoverTiempo():
    return QtGui.QIcon(pmMoverTiempo())


def pmMoverMas():
    return PM(216687,217726)


def MoverMas():
    return QtGui.QIcon(pmMoverMas())


def pmMoverGrabar():
    return PM(217726,218582)


def MoverGrabar():
    return QtGui.QIcon(pmMoverGrabar())


def pmMoverGrabarTodos():
    return PM(218582,219626)


def MoverGrabarTodos():
    return QtGui.QIcon(pmMoverGrabarTodos())


def pmMoverJugar():
    return PM(219626,220457)


def MoverJugar():
    return QtGui.QIcon(pmMoverJugar())


def pmPelicula():
    return PM(220457,222591)


def Pelicula():
    return QtGui.QIcon(pmPelicula())


def pmPelicula_Pausa():
    return PM(222591,224350)


def Pelicula_Pausa():
    return QtGui.QIcon(pmPelicula_Pausa())


def pmPelicula_Seguir():
    return PM(224350,226439)


def Pelicula_Seguir():
    return QtGui.QIcon(pmPelicula_Seguir())


def pmPelicula_Rapido():
    return PM(226439,228498)


def Pelicula_Rapido():
    return QtGui.QIcon(pmPelicula_Rapido())


def pmPelicula_Lento():
    return PM(228498,230373)


def Pelicula_Lento():
    return QtGui.QIcon(pmPelicula_Lento())


def pmPelicula_Repetir():
    return PM(37046,39340)


def Pelicula_Repetir():
    return QtGui.QIcon(pmPelicula_Repetir())


def pmPelicula_PGN():
    return PM(230373,231281)


def Pelicula_PGN():
    return QtGui.QIcon(pmPelicula_PGN())


def pmMemoria():
    return PM(231281,233222)


def Memoria():
    return QtGui.QIcon(pmMemoria())


def pmEntrenar():
    return PM(233222,234761)


def Entrenar():
    return QtGui.QIcon(pmEntrenar())


def pmEnviar():
    return PM(233222,234761)


def Enviar():
    return QtGui.QIcon(pmEnviar())


def pmBoxRooms():
    return PM(234761,239564)


def BoxRooms():
    return QtGui.QIcon(pmBoxRooms())


def pmBoxRoom():
    return PM(239564,240026)


def BoxRoom():
    return QtGui.QIcon(pmBoxRoom())


def pmNewBoxRoom():
    return PM(240026,241534)


def NewBoxRoom():
    return QtGui.QIcon(pmNewBoxRoom())


def pmNuevoMas():
    return PM(240026,241534)


def NuevoMas():
    return QtGui.QIcon(pmNuevoMas())


def pmTemas():
    return PM(241534,243757)


def Temas():
    return QtGui.QIcon(pmTemas())


def pmTutorialesCrear():
    return PM(243757,250026)


def TutorialesCrear():
    return QtGui.QIcon(pmTutorialesCrear())


def pmMover():
    return PM(250026,250608)


def Mover():
    return QtGui.QIcon(pmMover())


def pmSeleccionar():
    return PM(250608,256312)


def Seleccionar():
    return QtGui.QIcon(pmSeleccionar())


def pmVista():
    return PM(256312,258236)


def Vista():
    return QtGui.QIcon(pmVista())


def pmInformacionPGNUno():
    return PM(258236,259614)


def InformacionPGNUno():
    return QtGui.QIcon(pmInformacionPGNUno())


def pmDailyTest():
    return PM(259614,261954)


def DailyTest():
    return QtGui.QIcon(pmDailyTest())


def pmJuegaPorMi():
    return PM(261954,263674)


def JuegaPorMi():
    return QtGui.QIcon(pmJuegaPorMi())


def pmArbol():
    return PM(263674,264308)


def Arbol():
    return QtGui.QIcon(pmArbol())


def pmGrabarFichero():
    return PM(61313,62776)


def GrabarFichero():
    return QtGui.QIcon(pmGrabarFichero())


def pmClipboard():
    return PM(264308,265086)


def Clipboard():
    return QtGui.QIcon(pmClipboard())


def pmFics():
    return PM(265086,265503)


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
    return PM(265503,268855)


def Flechas():
    return QtGui.QIcon(pmFlechas())


def pmMarcos():
    return PM(268855,270302)


def Marcos():
    return QtGui.QIcon(pmMarcos())


def pmSVGs():
    return PM(270302,273871)


def SVGs():
    return QtGui.QIcon(pmSVGs())


def pmAmarillo():
    return PM(273871,275123)


def Amarillo():
    return QtGui.QIcon(pmAmarillo())


def pmNaranja():
    return PM(275123,276355)


def Naranja():
    return QtGui.QIcon(pmNaranja())


def pmVerde():
    return PM(276355,277631)


def Verde():
    return QtGui.QIcon(pmVerde())


def pmAzul():
    return PM(277631,278719)


def Azul():
    return QtGui.QIcon(pmAzul())


def pmMagenta():
    return PM(278719,280007)


def Magenta():
    return QtGui.QIcon(pmMagenta())


def pmRojo():
    return PM(280007,281226)


def Rojo():
    return QtGui.QIcon(pmRojo())


def pmGris():
    return PM(281226,282184)


def Gris():
    return QtGui.QIcon(pmGris())


def pmAmarillo32():
    return PM(282184,284164)


def Amarillo32():
    return QtGui.QIcon(pmAmarillo32())


def pmNaranja32():
    return PM(284164,286288)


def Naranja32():
    return QtGui.QIcon(pmNaranja32())


def pmVerde32():
    return PM(286288,288409)


def Verde32():
    return QtGui.QIcon(pmVerde32())


def pmAzul32():
    return PM(288409,290788)


def Azul32():
    return QtGui.QIcon(pmAzul32())


def pmMagenta32():
    return PM(290788,293239)


def Magenta32():
    return QtGui.QIcon(pmMagenta32())


def pmRojo32():
    return PM(293239,295054)


def Rojo32():
    return QtGui.QIcon(pmRojo32())


def pmGris32():
    return PM(295054,296968)


def Gris32():
    return QtGui.QIcon(pmGris32())


def pmPuntoBlanco():
    return PM(296968,297317)


def PuntoBlanco():
    return QtGui.QIcon(pmPuntoBlanco())


def pmPuntoAmarillo():
    return PM(212107,212569)


def PuntoAmarillo():
    return QtGui.QIcon(pmPuntoAmarillo())


def pmPuntoNaranja():
    return PM(297317,297779)


def PuntoNaranja():
    return QtGui.QIcon(pmPuntoNaranja())


def pmPuntoVerde():
    return PM(212892,213354)


def PuntoVerde():
    return QtGui.QIcon(pmPuntoVerde())


def pmPuntoAzul():
    return PM(239564,240026)


def PuntoAzul():
    return QtGui.QIcon(pmPuntoAzul())


def pmPuntoMagenta():
    return PM(297779,298278)


def PuntoMagenta():
    return QtGui.QIcon(pmPuntoMagenta())


def pmPuntoRojo():
    return PM(298278,298777)


def PuntoRojo():
    return QtGui.QIcon(pmPuntoRojo())


def pmPuntoNegro():
    return PM(212569,212892)


def PuntoNegro():
    return QtGui.QIcon(pmPuntoNegro())


def pmPuntoEstrella():
    return PM(298777,299204)


def PuntoEstrella():
    return QtGui.QIcon(pmPuntoEstrella())


def pmComentario():
    return PM(299204,299841)


def Comentario():
    return QtGui.QIcon(pmComentario())


def pmComentarioMas():
    return PM(299841,300780)


def ComentarioMas():
    return QtGui.QIcon(pmComentarioMas())


def pmComentarioEditar():
    return PM(217726,218582)


def ComentarioEditar():
    return QtGui.QIcon(pmComentarioEditar())


def pmOpeningComentario():
    return PM(300780,301776)


def OpeningComentario():
    return QtGui.QIcon(pmOpeningComentario())


def pmMas():
    return PM(301776,302285)


def Mas():
    return QtGui.QIcon(pmMas())


def pmMasR():
    return PM(302285,302773)


def MasR():
    return QtGui.QIcon(pmMasR())


def pmMasDoc():
    return PM(302773,303574)


def MasDoc():
    return QtGui.QIcon(pmMasDoc())


def pmPotencia():
    return PM(177799,178665)


def Potencia():
    return QtGui.QIcon(pmPotencia())


def pmBMT():
    return PM(303574,304452)


def BMT():
    return QtGui.QIcon(pmBMT())


def pmOjo():
    return PM(304452,305574)


def Ojo():
    return QtGui.QIcon(pmOjo())


def pmOcultar():
    return PM(304452,305574)


def Ocultar():
    return QtGui.QIcon(pmOcultar())


def pmMostrar():
    return PM(305574,306630)


def Mostrar():
    return QtGui.QIcon(pmMostrar())


def pmBlog():
    return PM(306630,307152)


def Blog():
    return QtGui.QIcon(pmBlog())


def pmVariations():
    return PM(307152,308059)


def Variations():
    return QtGui.QIcon(pmVariations())


def pmVariationsG():
    return PM(308059,310486)


def VariationsG():
    return QtGui.QIcon(pmVariationsG())


def pmCambiar():
    return PM(310486,312200)


def Cambiar():
    return QtGui.QIcon(pmCambiar())


def pmAnterior():
    return PM(312200,314254)


def Anterior():
    return QtGui.QIcon(pmAnterior())


def pmSiguiente():
    return PM(314254,316324)


def Siguiente():
    return QtGui.QIcon(pmSiguiente())


def pmSiguienteF():
    return PM(316324,318499)


def SiguienteF():
    return QtGui.QIcon(pmSiguienteF())


def pmAnteriorF():
    return PM(318499,320693)


def AnteriorF():
    return QtGui.QIcon(pmAnteriorF())


def pmX():
    return PM(320693,321975)


def X():
    return QtGui.QIcon(pmX())


def pmTools():
    return PM(321975,324576)


def Tools():
    return QtGui.QIcon(pmTools())


def pmTacticas():
    return PM(324576,327149)


def Tacticas():
    return QtGui.QIcon(pmTacticas())


def pmCancelarPeque():
    return PM(327149,327711)


def CancelarPeque():
    return QtGui.QIcon(pmCancelarPeque())


def pmAceptarPeque():
    return PM(213354,214371)


def AceptarPeque():
    return QtGui.QIcon(pmAceptarPeque())


def pmLibre():
    return PM(327711,330103)


def Libre():
    return QtGui.QIcon(pmLibre())


def pmEnBlanco():
    return PM(330103,330829)


def EnBlanco():
    return QtGui.QIcon(pmEnBlanco())


def pmDirector():
    return PM(330829,333803)


def Director():
    return QtGui.QIcon(pmDirector())


def pmTorneos():
    return PM(333803,335541)


def Torneos():
    return QtGui.QIcon(pmTorneos())


def pmOpenings():
    return PM(335541,336466)


def Openings():
    return QtGui.QIcon(pmOpenings())


def pmV_Blancas():
    return PM(336466,336746)


def V_Blancas():
    return QtGui.QIcon(pmV_Blancas())


def pmV_Blancas_Mas():
    return PM(336746,337026)


def V_Blancas_Mas():
    return QtGui.QIcon(pmV_Blancas_Mas())


def pmV_Blancas_Mas_Mas():
    return PM(337026,337298)


def V_Blancas_Mas_Mas():
    return QtGui.QIcon(pmV_Blancas_Mas_Mas())


def pmV_Negras():
    return PM(337298,337573)


def V_Negras():
    return QtGui.QIcon(pmV_Negras())


def pmV_Negras_Mas():
    return PM(337573,337848)


def V_Negras_Mas():
    return QtGui.QIcon(pmV_Negras_Mas())


def pmV_Negras_Mas_Mas():
    return PM(337848,338117)


def V_Negras_Mas_Mas():
    return QtGui.QIcon(pmV_Negras_Mas_Mas())


def pmV_Blancas_Igual_Negras():
    return PM(338117,338419)


def V_Blancas_Igual_Negras():
    return QtGui.QIcon(pmV_Blancas_Igual_Negras())


def pmMezclar():
    return PM(135834,138230)


def Mezclar():
    return QtGui.QIcon(pmMezclar())


def pmVoyager():
    return PM(338419,339262)


def Voyager():
    return QtGui.QIcon(pmVoyager())


def pmVoyager32():
    return PM(339262,341150)


def Voyager32():
    return QtGui.QIcon(pmVoyager32())


def pmReindexar():
    return PM(341150,342967)


def Reindexar():
    return QtGui.QIcon(pmReindexar())


def pmRename():
    return PM(342967,343951)


def Rename():
    return QtGui.QIcon(pmRename())


def pmAdd():
    return PM(343951,344904)


def Add():
    return QtGui.QIcon(pmAdd())


def pmMas22():
    return PM(344904,345568)


def Mas22():
    return QtGui.QIcon(pmMas22())


def pmMenos22():
    return PM(345568,346012)


def Menos22():
    return QtGui.QIcon(pmMenos22())


def pmTransposition():
    return PM(346012,346531)


def Transposition():
    return QtGui.QIcon(pmTransposition())


def pmRat():
    return PM(346531,352235)


def Rat():
    return QtGui.QIcon(pmRat())


def pmAlligator():
    return PM(352235,357227)


def Alligator():
    return QtGui.QIcon(pmAlligator())


def pmAnt():
    return PM(357227,363925)


def Ant():
    return QtGui.QIcon(pmAnt())


def pmBat():
    return PM(363925,366879)


def Bat():
    return QtGui.QIcon(pmBat())


def pmBear():
    return PM(366879,374158)


def Bear():
    return QtGui.QIcon(pmBear())


def pmBee():
    return PM(374158,379160)


def Bee():
    return QtGui.QIcon(pmBee())


def pmBird():
    return PM(379160,385219)


def Bird():
    return QtGui.QIcon(pmBird())


def pmBull():
    return PM(385219,392188)


def Bull():
    return QtGui.QIcon(pmBull())


def pmBulldog():
    return PM(392188,399079)


def Bulldog():
    return QtGui.QIcon(pmBulldog())


def pmButterfly():
    return PM(399079,406453)


def Butterfly():
    return QtGui.QIcon(pmButterfly())


def pmCat():
    return PM(406453,412725)


def Cat():
    return QtGui.QIcon(pmCat())


def pmChicken():
    return PM(412725,418536)


def Chicken():
    return QtGui.QIcon(pmChicken())


def pmCow():
    return PM(418536,425279)


def Cow():
    return QtGui.QIcon(pmCow())


def pmCrab():
    return PM(425279,430868)


def Crab():
    return QtGui.QIcon(pmCrab())


def pmCrocodile():
    return PM(430868,437009)


def Crocodile():
    return QtGui.QIcon(pmCrocodile())


def pmDeer():
    return PM(437009,443316)


def Deer():
    return QtGui.QIcon(pmDeer())


def pmDog():
    return PM(443316,449919)


def Dog():
    return QtGui.QIcon(pmDog())


def pmDonkey():
    return PM(449919,455566)


def Donkey():
    return QtGui.QIcon(pmDonkey())


def pmDuck():
    return PM(455566,462109)


def Duck():
    return QtGui.QIcon(pmDuck())


def pmEagle():
    return PM(462109,466927)


def Eagle():
    return QtGui.QIcon(pmEagle())


def pmElephant():
    return PM(466927,473408)


def Elephant():
    return QtGui.QIcon(pmElephant())


def pmFish():
    return PM(473408,480249)


def Fish():
    return QtGui.QIcon(pmFish())


def pmFox():
    return PM(480249,487032)


def Fox():
    return QtGui.QIcon(pmFox())


def pmFrog():
    return PM(487032,493448)


def Frog():
    return QtGui.QIcon(pmFrog())


def pmGiraffe():
    return PM(493448,500626)


def Giraffe():
    return QtGui.QIcon(pmGiraffe())


def pmGorilla():
    return PM(500626,507165)


def Gorilla():
    return QtGui.QIcon(pmGorilla())


def pmHippo():
    return PM(507165,514286)


def Hippo():
    return QtGui.QIcon(pmHippo())


def pmHorse():
    return PM(514286,520833)


def Horse():
    return QtGui.QIcon(pmHorse())


def pmInsect():
    return PM(520833,526768)


def Insect():
    return QtGui.QIcon(pmInsect())


def pmLion():
    return PM(526768,535678)


def Lion():
    return QtGui.QIcon(pmLion())


def pmMonkey():
    return PM(535678,543357)


def Monkey():
    return QtGui.QIcon(pmMonkey())


def pmMoose():
    return PM(543357,549981)


def Moose():
    return QtGui.QIcon(pmMoose())


def pmMouse():
    return PM(346531,352235)


def Mouse():
    return QtGui.QIcon(pmMouse())


def pmOwl():
    return PM(549981,556687)


def Owl():
    return QtGui.QIcon(pmOwl())


def pmPanda():
    return PM(556687,560721)


def Panda():
    return QtGui.QIcon(pmPanda())


def pmPenguin():
    return PM(560721,566270)


def Penguin():
    return QtGui.QIcon(pmPenguin())


def pmPig():
    return PM(566270,574310)


def Pig():
    return QtGui.QIcon(pmPig())


def pmRabbit():
    return PM(574310,581611)


def Rabbit():
    return QtGui.QIcon(pmRabbit())


def pmRhino():
    return PM(581611,587998)


def Rhino():
    return QtGui.QIcon(pmRhino())


def pmRooster():
    return PM(587998,593261)


def Rooster():
    return QtGui.QIcon(pmRooster())


def pmShark():
    return PM(593261,599031)


def Shark():
    return QtGui.QIcon(pmShark())


def pmSheep():
    return PM(599031,602862)


def Sheep():
    return QtGui.QIcon(pmSheep())


def pmSnake():
    return PM(602862,608887)


def Snake():
    return QtGui.QIcon(pmSnake())


def pmTiger():
    return PM(608887,616924)


def Tiger():
    return QtGui.QIcon(pmTiger())


def pmTurkey():
    return PM(616924,624338)


def Turkey():
    return QtGui.QIcon(pmTurkey())


def pmTurtle():
    return PM(624338,631059)


def Turtle():
    return QtGui.QIcon(pmTurtle())


def pmWolf():
    return PM(631059,634154)


def Wolf():
    return QtGui.QIcon(pmWolf())


def pmSteven():
    return PM(634154,637814)


def Steven():
    return QtGui.QIcon(pmSteven())


def pmKnightMan():
    return PM(637814,644966)


def KnightMan():
    return QtGui.QIcon(pmKnightMan())


def pmWheel():
    return PM(644966,653031)


def Wheel():
    return QtGui.QIcon(pmWheel())


def pmWheelchair():
    return PM(653031,661835)


def Wheelchair():
    return QtGui.QIcon(pmWheelchair())


def pmTouringMotorcycle():
    return PM(661835,668147)


def TouringMotorcycle():
    return QtGui.QIcon(pmTouringMotorcycle())


def pmContainer():
    return PM(668147,673482)


def Container():
    return QtGui.QIcon(pmContainer())


def pmBoatEquipment():
    return PM(673482,679005)


def BoatEquipment():
    return QtGui.QIcon(pmBoatEquipment())


def pmCar():
    return PM(679005,683651)


def Car():
    return QtGui.QIcon(pmCar())


def pmLorry():
    return PM(683651,689687)


def Lorry():
    return QtGui.QIcon(pmLorry())


def pmCarTrailer():
    return PM(689687,693784)


def CarTrailer():
    return QtGui.QIcon(pmCarTrailer())


def pmTowTruck():
    return PM(693784,698542)


def TowTruck():
    return QtGui.QIcon(pmTowTruck())


def pmQuadBike():
    return PM(698542,704511)


def QuadBike():
    return QtGui.QIcon(pmQuadBike())


def pmRecoveryTruck():
    return PM(704511,709508)


def RecoveryTruck():
    return QtGui.QIcon(pmRecoveryTruck())


def pmContainerLoader():
    return PM(709508,714650)


def ContainerLoader():
    return QtGui.QIcon(pmContainerLoader())


def pmPoliceCar():
    return PM(714650,719482)


def PoliceCar():
    return QtGui.QIcon(pmPoliceCar())


def pmExecutiveCar():
    return PM(719482,724160)


def ExecutiveCar():
    return QtGui.QIcon(pmExecutiveCar())


def pmTruck():
    return PM(724160,729623)


def Truck():
    return QtGui.QIcon(pmTruck())


def pmExcavator():
    return PM(729623,734514)


def Excavator():
    return QtGui.QIcon(pmExcavator())


def pmCabriolet():
    return PM(734514,739352)


def Cabriolet():
    return QtGui.QIcon(pmCabriolet())


def pmMixerTruck():
    return PM(739352,745662)


def MixerTruck():
    return QtGui.QIcon(pmMixerTruck())


def pmForkliftTruckLoaded():
    return PM(745662,751810)


def ForkliftTruckLoaded():
    return QtGui.QIcon(pmForkliftTruckLoaded())


def pmAmbulance():
    return PM(751810,757860)


def Ambulance():
    return QtGui.QIcon(pmAmbulance())


def pmDieselLocomotiveBoxcar():
    return PM(757860,761866)


def DieselLocomotiveBoxcar():
    return QtGui.QIcon(pmDieselLocomotiveBoxcar())


def pmTractorUnit():
    return PM(761866,767333)


def TractorUnit():
    return QtGui.QIcon(pmTractorUnit())


def pmFireTruck():
    return PM(767333,773672)


def FireTruck():
    return QtGui.QIcon(pmFireTruck())


def pmCargoShip():
    return PM(773672,778013)


def CargoShip():
    return QtGui.QIcon(pmCargoShip())


def pmSubwayTrain():
    return PM(778013,782903)


def SubwayTrain():
    return QtGui.QIcon(pmSubwayTrain())


def pmTruckMountedCrane():
    return PM(782903,788644)


def TruckMountedCrane():
    return QtGui.QIcon(pmTruckMountedCrane())


def pmAirAmbulance():
    return PM(788644,793757)


def AirAmbulance():
    return QtGui.QIcon(pmAirAmbulance())


def pmAirplane():
    return PM(793757,798645)


def Airplane():
    return QtGui.QIcon(pmAirplane())


def pmCaracol():
    return PM(798645,800461)


def Caracol():
    return QtGui.QIcon(pmCaracol())


def pmUno():
    return PM(800461,802923)


def Uno():
    return QtGui.QIcon(pmUno())


def pmMotoresExternos():
    return PM(802923,804825)


def MotoresExternos():
    return QtGui.QIcon(pmMotoresExternos())


def pmDatabase():
    return PM(804825,806141)


def Database():
    return QtGui.QIcon(pmDatabase())


def pmDatabaseMas():
    return PM(806141,807600)


def DatabaseMas():
    return QtGui.QIcon(pmDatabaseMas())


def pmDatabaseImport():
    return PM(807600,808236)


def DatabaseImport():
    return QtGui.QIcon(pmDatabaseImport())


def pmDatabaseExport():
    return PM(808236,808881)


def DatabaseExport():
    return QtGui.QIcon(pmDatabaseExport())


def pmDatabaseDelete():
    return PM(808881,810004)


def DatabaseDelete():
    return QtGui.QIcon(pmDatabaseDelete())


def pmDatabaseMaintenance():
    return PM(810004,811500)


def DatabaseMaintenance():
    return QtGui.QIcon(pmDatabaseMaintenance())


def pmAtacante():
    return PM(811500,812105)


def Atacante():
    return QtGui.QIcon(pmAtacante())


def pmAtacada():
    return PM(812105,812671)


def Atacada():
    return QtGui.QIcon(pmAtacada())


def pmGoToNext():
    return PM(812671,813083)


def GoToNext():
    return QtGui.QIcon(pmGoToNext())


def pmBlancas():
    return PM(813083,813434)


def Blancas():
    return QtGui.QIcon(pmBlancas())


def pmNegras():
    return PM(813434,813680)


def Negras():
    return QtGui.QIcon(pmNegras())


def pmFolderChange():
    return PM(64828,67586)


def FolderChange():
    return QtGui.QIcon(pmFolderChange())


def pmMarkers():
    return PM(813680,815375)


def Markers():
    return QtGui.QIcon(pmMarkers())


def pmTop():
    return PM(815375,815959)


def Top():
    return QtGui.QIcon(pmTop())


def pmBottom():
    return PM(815959,816548)


def Bottom():
    return QtGui.QIcon(pmBottom())


def pmSTS():
    return PM(816548,818739)


def STS():
    return QtGui.QIcon(pmSTS())


def pmRun():
    return PM(818739,820463)


def Run():
    return QtGui.QIcon(pmRun())


def pmRun2():
    return PM(820463,821983)


def Run2():
    return QtGui.QIcon(pmRun2())


def pmWorldMap():
    return PM(821983,824724)


def WorldMap():
    return QtGui.QIcon(pmWorldMap())


def pmAfrica():
    return PM(824724,827210)


def Africa():
    return QtGui.QIcon(pmAfrica())


def pmMaps():
    return PM(827210,828154)


def Maps():
    return QtGui.QIcon(pmMaps())


def pmSol():
    return PM(828154,829080)


def Sol():
    return QtGui.QIcon(pmSol())


def pmSolNubes():
    return PM(829080,829943)


def SolNubes():
    return QtGui.QIcon(pmSolNubes())


def pmSolNubesLluvia():
    return PM(829943,830903)


def SolNubesLluvia():
    return QtGui.QIcon(pmSolNubesLluvia())


def pmLluvia():
    return PM(830903,831742)


def Lluvia():
    return QtGui.QIcon(pmLluvia())


def pmInvierno():
    return PM(831742,833318)


def Invierno():
    return QtGui.QIcon(pmInvierno())


def pmFixedElo():
    return PM(158145,159408)


def FixedElo():
    return QtGui.QIcon(pmFixedElo())


def pmSoundTool():
    return PM(833318,835777)


def SoundTool():
    return QtGui.QIcon(pmSoundTool())


def pmTrain():
    return PM(835777,837147)


def Train():
    return QtGui.QIcon(pmTrain())


def pmPlay():
    return PM(224350,226439)


def Play():
    return QtGui.QIcon(pmPlay())


def pmMeasure():
    return PM(119930,121553)


def Measure():
    return QtGui.QIcon(pmMeasure())


def pmPlayGame():
    return PM(837147,841505)


def PlayGame():
    return QtGui.QIcon(pmPlayGame())


def pmScanner():
    return PM(841505,841846)


def Scanner():
    return QtGui.QIcon(pmScanner())


def pmCursorScanner():
    return PM(841846,842163)


def CursorScanner():
    return QtGui.QIcon(pmCursorScanner())


def pmMenos():
    return PM(842163,842688)


def Menos():
    return QtGui.QIcon(pmMenos())


def pmSchool():
    return PM(842688,844050)


def School():
    return QtGui.QIcon(pmSchool())


def pmLaw():
    return PM(844050,844666)


def Law():
    return QtGui.QIcon(pmLaw())


def pmLearnGame():
    return PM(844666,845099)


def LearnGame():
    return QtGui.QIcon(pmLearnGame())


def pmLonghaul():
    return PM(845099,846025)


def Longhaul():
    return QtGui.QIcon(pmLonghaul())


def pmTrekking():
    return PM(846025,846719)


def Trekking():
    return QtGui.QIcon(pmTrekking())


def pmPassword():
    return PM(846719,847172)


def Password():
    return QtGui.QIcon(pmPassword())


def pmSQL_RAW():
    return PM(837147,841505)


def SQL_RAW():
    return QtGui.QIcon(pmSQL_RAW())


def pmSun():
    return PM(303574,304452)


def Sun():
    return QtGui.QIcon(pmSun())


def pmLight32():
    return PM(847172,848872)


def Light32():
    return QtGui.QIcon(pmLight32())


def pmTOL():
    return PM(848872,849581)


def TOL():
    return QtGui.QIcon(pmTOL())


def pmUned():
    return PM(849581,850001)


def Uned():
    return QtGui.QIcon(pmUned())


def pmUwe():
    return PM(850001,850970)


def Uwe():
    return QtGui.QIcon(pmUwe())


def pmThinking():
    return PM(850970,851759)


def Thinking():
    return QtGui.QIcon(pmThinking())


def pmWashingMachine():
    return PM(851759,852422)


def WashingMachine():
    return QtGui.QIcon(pmWashingMachine())


def pmTerminal():
    return PM(852422,855966)


def Terminal():
    return QtGui.QIcon(pmTerminal())


def pmManualSave():
    return PM(855966,856549)


def ManualSave():
    return QtGui.QIcon(pmManualSave())


def pmSettings():
    return PM(856549,856987)


def Settings():
    return QtGui.QIcon(pmSettings())


def pmStrength():
    return PM(856987,857658)


def Strength():
    return QtGui.QIcon(pmStrength())


def pmSingular():
    return PM(857658,858513)


def Singular():
    return QtGui.QIcon(pmSingular())


def pmScript():
    return PM(858513,859082)


def Script():
    return QtGui.QIcon(pmScript())


def pmTexto():
    return PM(859082,861927)


def Texto():
    return QtGui.QIcon(pmTexto())


def pmLampara():
    return PM(861927,862636)


def Lampara():
    return QtGui.QIcon(pmLampara())


def pmFile():
    return PM(862636,864936)


def File():
    return QtGui.QIcon(pmFile())


def pmCalculo():
    return PM(864936,865862)


def Calculo():
    return QtGui.QIcon(pmCalculo())


def pmOpeningLines():
    return PM(865862,866540)


def OpeningLines():
    return QtGui.QIcon(pmOpeningLines())


def pmStudy():
    return PM(866540,867453)


def Study():
    return QtGui.QIcon(pmStudy())


def pmLichess():
    return PM(867453,868341)


def Lichess():
    return QtGui.QIcon(pmLichess())


def pmMiniatura():
    return PM(868341,869268)


def Miniatura():
    return QtGui.QIcon(pmMiniatura())


def pmLocomotora():
    return PM(869268,870049)


def Locomotora():
    return QtGui.QIcon(pmLocomotora())


def pmTrainSequential():
    return PM(870049,871190)


def TrainSequential():
    return QtGui.QIcon(pmTrainSequential())


def pmTrainStatic():
    return PM(871190,872150)


def TrainStatic():
    return QtGui.QIcon(pmTrainStatic())


def pmTrainPositions():
    return PM(872150,873131)


def TrainPositions():
    return QtGui.QIcon(pmTrainPositions())


def pmTrainEngines():
    return PM(873131,874565)


def TrainEngines():
    return QtGui.QIcon(pmTrainEngines())


def pmError():
    return PM(41940,45940)


def Error():
    return QtGui.QIcon(pmError())


def pmAtajos():
    return PM(874565,875744)


def Atajos():
    return QtGui.QIcon(pmAtajos())


def pmTOLline():
    return PM(875744,876848)


def TOLline():
    return QtGui.QIcon(pmTOLline())


def pmTOLchange():
    return PM(876848,879070)


def TOLchange():
    return QtGui.QIcon(pmTOLchange())


def pmPack():
    return PM(879070,880243)


def Pack():
    return QtGui.QIcon(pmPack())


def pmHome():
    return PM(173155,174337)


def Home():
    return QtGui.QIcon(pmHome())


def pmImport8():
    return PM(880243,881165)


def Import8():
    return QtGui.QIcon(pmImport8())


def pmExport8():
    return PM(881165,882065)


def Export8():
    return QtGui.QIcon(pmExport8())


def pmTablas8():
    return PM(882065,882857)


def Tablas8():
    return QtGui.QIcon(pmTablas8())


def pmBlancas8():
    return PM(882857,883887)


def Blancas8():
    return QtGui.QIcon(pmBlancas8())


def pmNegras8():
    return PM(883887,884726)


def Negras8():
    return QtGui.QIcon(pmNegras8())


def pmBook():
    return PM(884726,885300)


def Book():
    return QtGui.QIcon(pmBook())


def pmWrite():
    return PM(885300,886505)


def Write():
    return QtGui.QIcon(pmWrite())


def pmAlt():
    return PM(886505,886947)


def Alt():
    return QtGui.QIcon(pmAlt())


def pmShift():
    return PM(886947,887287)


def Shift():
    return QtGui.QIcon(pmShift())


def pmRightMouse():
    return PM(887287,888087)


def RightMouse():
    return QtGui.QIcon(pmRightMouse())


def pmControl():
    return PM(888087,888612)


def Control():
    return QtGui.QIcon(pmControl())


def pmFinales():
    return PM(888612,889699)


def Finales():
    return QtGui.QIcon(pmFinales())


def pmEditColumns():
    return PM(889699,890431)


def EditColumns():
    return QtGui.QIcon(pmEditColumns())


def pmResizeAll():
    return PM(890431,890941)


def ResizeAll():
    return QtGui.QIcon(pmResizeAll())


def pmChecked():
    return PM(890941,891447)


def Checked():
    return QtGui.QIcon(pmChecked())


def pmUnchecked():
    return PM(891447,891695)


def Unchecked():
    return QtGui.QIcon(pmUnchecked())


def pmBuscarC():
    return PM(891695,892139)


def BuscarC():
    return QtGui.QIcon(pmBuscarC())


def pmPeonBlanco():
    return PM(892139,894320)


def PeonBlanco():
    return QtGui.QIcon(pmPeonBlanco())


def pmPeonNegro():
    return PM(894320,895844)


def PeonNegro():
    return QtGui.QIcon(pmPeonNegro())


def pmReciclar():
    return PM(895844,896568)


def Reciclar():
    return QtGui.QIcon(pmReciclar())


def pmLanzamiento():
    return PM(896568,897281)


def Lanzamiento():
    return QtGui.QIcon(pmLanzamiento())


def pmLanzamientos():
    return PM(897281,897875)


def Lanzamientos():
    return QtGui.QIcon(pmLanzamientos())


def pmEndGame():
    return PM(897875,898289)


def EndGame():
    return QtGui.QIcon(pmEndGame())


def pmPause():
    return PM(898289,899158)


def Pause():
    return QtGui.QIcon(pmPause())


def pmContinue():
    return PM(899158,900362)


def Continue():
    return QtGui.QIcon(pmContinue())


def pmClose():
    return PM(900362,901061)


def Close():
    return QtGui.QIcon(pmClose())


def pmStop():
    return PM(901061,902094)


def Stop():
    return QtGui.QIcon(pmStop())


def pmFactoryPolyglot():
    return PM(902094,902914)


def FactoryPolyglot():
    return QtGui.QIcon(pmFactoryPolyglot())


def pmTags():
    return PM(902914,903737)


def Tags():
    return QtGui.QIcon(pmTags())


def pmAppearance():
    return PM(903737,904464)


def Appearance():
    return QtGui.QIcon(pmAppearance())


def pmFill():
    return PM(904464,905502)


def Fill():
    return QtGui.QIcon(pmFill())


def pmSupport():
    return PM(905502,906234)


def Support():
    return QtGui.QIcon(pmSupport())


def pmOrder():
    return PM(906234,907032)


def Order():
    return QtGui.QIcon(pmOrder())


def pmPlay1():
    return PM(907032,908327)


def Play1():
    return QtGui.QIcon(pmPlay1())


def pmRemove1():
    return PM(908327,909454)


def Remove1():
    return QtGui.QIcon(pmRemove1())


def pmNew1():
    return PM(909454,909776)


def New1():
    return QtGui.QIcon(pmNew1())


def pmMensError():
    return PM(909776,911840)


def MensError():
    return QtGui.QIcon(pmMensError())


def pmMensInfo():
    return PM(911840,914395)


def MensInfo():
    return QtGui.QIcon(pmMensInfo())


def pmJump():
    return PM(914395,915070)


def Jump():
    return QtGui.QIcon(pmJump())


def pmCaptures():
    return PM(915070,916251)


def Captures():
    return QtGui.QIcon(pmCaptures())


def pmRepeat():
    return PM(916251,916910)


def Repeat():
    return QtGui.QIcon(pmRepeat())


def pmCount():
    return PM(916910,917586)


def Count():
    return QtGui.QIcon(pmCount())


def pmMate15():
    return PM(917586,918657)


def Mate15():
    return QtGui.QIcon(pmMate15())


def pmCoordinates():
    return PM(918657,919810)


def Coordinates():
    return QtGui.QIcon(pmCoordinates())


def pmKnight():
    return PM(919810,921053)


def Knight():
    return QtGui.QIcon(pmKnight())


def pmCorrecto():
    return PM(921053,922079)


def Correcto():
    return QtGui.QIcon(pmCorrecto())


def pmBlocks():
    return PM(922079,922416)


def Blocks():
    return QtGui.QIcon(pmBlocks())


def pmWest():
    return PM(922416,923522)


def West():
    return QtGui.QIcon(pmWest())


def pmOpening():
    return PM(923522,923780)


def Opening():
    return QtGui.QIcon(pmOpening())


def pmVariation():
    return PM(215690,216108)


def Variation():
    return QtGui.QIcon(pmVariation())


def pmComment():
    return PM(923780,924143)


def Comment():
    return QtGui.QIcon(pmComment())


def pmComment32():
    return PM(924143,925110)


def Comment32():
    return QtGui.QIcon(pmComment32())


def pmVariationComment():
    return PM(925110,925454)


def VariationComment():
    return QtGui.QIcon(pmVariationComment())


def pmOpeningVariation():
    return PM(925454,925918)


def OpeningVariation():
    return QtGui.QIcon(pmOpeningVariation())


def pmOpeningComment():
    return PM(925918,926251)


def OpeningComment():
    return QtGui.QIcon(pmOpeningComment())


def pmOpeningVariationComment():
    return PM(925454,925918)


def OpeningVariationComment():
    return QtGui.QIcon(pmOpeningVariationComment())


def pmDeleteRow():
    return PM(926251,926682)


def DeleteRow():
    return QtGui.QIcon(pmDeleteRow())


def pmDeleteColumn():
    return PM(926682,927125)


def DeleteColumn():
    return QtGui.QIcon(pmDeleteColumn())


def pmEditVariation():
    return PM(927125,927480)


def EditVariation():
    return QtGui.QIcon(pmEditVariation())


def pmKibitzer():
    return PM(927480,928079)


def Kibitzer():
    return QtGui.QIcon(pmKibitzer())


def pmKibitzer_Pause():
    return PM(928079,928251)


def Kibitzer_Pause():
    return QtGui.QIcon(pmKibitzer_Pause())


def pmKibitzer_Options():
    return PM(928251,929153)


def Kibitzer_Options():
    return QtGui.QIcon(pmKibitzer_Options())


def pmKibitzer_Voyager():
    return PM(338419,339262)


def Kibitzer_Voyager():
    return QtGui.QIcon(pmKibitzer_Voyager())


def pmKibitzer_Close():
    return PM(929153,929710)


def Kibitzer_Close():
    return QtGui.QIcon(pmKibitzer_Close())


def pmKibitzer_Down():
    return PM(929710,930099)


def Kibitzer_Down():
    return QtGui.QIcon(pmKibitzer_Down())


def pmKibitzer_Up():
    return PM(930099,930494)


def Kibitzer_Up():
    return QtGui.QIcon(pmKibitzer_Up())


def pmKibitzer_Back():
    return PM(930494,930927)


def Kibitzer_Back():
    return QtGui.QIcon(pmKibitzer_Back())


def pmKibitzer_Clipboard():
    return PM(930927,931313)


def Kibitzer_Clipboard():
    return QtGui.QIcon(pmKibitzer_Clipboard())


def pmKibitzer_Play():
    return PM(931313,931834)


def Kibitzer_Play():
    return QtGui.QIcon(pmKibitzer_Play())


def pmKibitzer_Side():
    return PM(931834,932587)


def Kibitzer_Side():
    return QtGui.QIcon(pmKibitzer_Side())


def pmKibitzer_Board():
    return PM(932587,933025)


def Kibitzer_Board():
    return QtGui.QIcon(pmKibitzer_Board())


def pmBoard():
    return PM(933025,933494)


def Board():
    return QtGui.QIcon(pmBoard())


def pmTraining_Games():
    return PM(933494,935186)


def Training_Games():
    return QtGui.QIcon(pmTraining_Games())


def pmTraining_Basic():
    return PM(935186,936559)


def Training_Basic():
    return QtGui.QIcon(pmTraining_Basic())


def pmTraining_Tactics():
    return PM(936559,937340)


def Training_Tactics():
    return QtGui.QIcon(pmTraining_Tactics())


def pmTraining_Endings():
    return PM(937340,938274)


def Training_Endings():
    return QtGui.QIcon(pmTraining_Endings())


def pmBridge():
    return PM(938274,939292)


def Bridge():
    return QtGui.QIcon(pmBridge())


def pmMaia():
    return PM(939292,940076)


def Maia():
    return QtGui.QIcon(pmMaia())


def pmBinBook():
    return PM(940076,940825)


def BinBook():
    return QtGui.QIcon(pmBinBook())


def pmConnected():
    return PM(940825,941054)


def Connected():
    return QtGui.QIcon(pmConnected())


def pmThemes():
    return PM(941054,941623)


def Themes():
    return QtGui.QIcon(pmThemes())


def pmReset():
    return PM(941623,943242)


def Reset():
    return QtGui.QIcon(pmReset())


def pmInstall():
    return PM(943242,945371)


def Install():
    return QtGui.QIcon(pmInstall())


def pmUninstall():
    return PM(945371,947397)


def Uninstall():
    return QtGui.QIcon(pmUninstall())


def pmLive():
    return PM(947397,950880)


def Live():
    return QtGui.QIcon(pmLive())


def pmLauncher():
    return PM(950880,955555)


def Launcher():
    return QtGui.QIcon(pmLauncher())


def pmLogInactive():
    return PM(955555,956086)


def LogInactive():
    return QtGui.QIcon(pmLogInactive())


def pmLogActive():
    return PM(956086,956650)


def LogActive():
    return QtGui.QIcon(pmLogActive())


def pmFolderAnil():
    return PM(956650,957014)


def FolderAnil():
    return QtGui.QIcon(pmFolderAnil())


def pmFolderBlack():
    return PM(957014,957351)


def FolderBlack():
    return QtGui.QIcon(pmFolderBlack())


def pmFolderBlue():
    return PM(957351,957725)


def FolderBlue():
    return QtGui.QIcon(pmFolderBlue())


def pmFolderGreen():
    return PM(957725,958097)


def FolderGreen():
    return QtGui.QIcon(pmFolderGreen())


def pmFolderMagenta():
    return PM(958097,958470)


def FolderMagenta():
    return QtGui.QIcon(pmFolderMagenta())


def pmFolderRed():
    return PM(958470,958834)


def FolderRed():
    return QtGui.QIcon(pmFolderRed())


def pmThis():
    return PM(958834,959288)


def This():
    return QtGui.QIcon(pmThis())


def pmAll():
    return PM(959288,959791)


def All():
    return QtGui.QIcon(pmAll())


def pmPrevious():
    return PM(959791,960250)


def Previous():
    return QtGui.QIcon(pmPrevious())


def pmLine():
    return PM(960250,960437)


def Line():
    return QtGui.QIcon(pmLine())


def pmEmpty():
    return PM(960437,960522)


def Empty():
    return QtGui.QIcon(pmEmpty())


def pmMore():
    return PM(960522,960811)


def More():
    return QtGui.QIcon(pmMore())


def pmSelectLogo():
    return PM(960811,961417)


def SelectLogo():
    return QtGui.QIcon(pmSelectLogo())


def pmSelect():
    return PM(961417,962071)


def Select():
    return QtGui.QIcon(pmSelect())


def pmSelectClose():
    return PM(962071,962843)


def SelectClose():
    return QtGui.QIcon(pmSelectClose())


def pmSelectHome():
    return PM(962843,963625)


def SelectHome():
    return QtGui.QIcon(pmSelectHome())


def pmSelectHistory():
    return PM(963625,964177)


def SelectHistory():
    return QtGui.QIcon(pmSelectHistory())


def pmSelectExplorer():
    return PM(964177,964910)


def SelectExplorer():
    return QtGui.QIcon(pmSelectExplorer())


def pmSelectFolderCreate():
    return PM(964910,965829)


def SelectFolderCreate():
    return QtGui.QIcon(pmSelectFolderCreate())


def pmSelectFolderRemove():
    return PM(965829,966856)


def SelectFolderRemove():
    return QtGui.QIcon(pmSelectFolderRemove())


def pmSelectReload():
    return PM(966856,968510)


def SelectReload():
    return QtGui.QIcon(pmSelectReload())


def pmSelectAccept():
    return PM(968510,969311)


def SelectAccept():
    return QtGui.QIcon(pmSelectAccept())


def pmWiki():
    return PM(969311,970428)


def Wiki():
    return QtGui.QIcon(pmWiki())


def pmCircle():
    return PM(970428,971888)


def Circle():
    return QtGui.QIcon(pmCircle())


def pmSortAZ():
    return PM(971888,972652)


def SortAZ():
    return QtGui.QIcon(pmSortAZ())


def pmReference():
    return PM(972652,973763)


def Reference():
    return QtGui.QIcon(pmReference())


def pmLanguageNew():
    return PM(973763,974490)


def LanguageNew():
    return QtGui.QIcon(pmLanguageNew())


def pmODT():
    return PM(974490,975605)


def ODT():
    return QtGui.QIcon(pmODT())


def pmEngines():
    return PM(975605,977091)


def Engines():
    return QtGui.QIcon(pmEngines())


def pmConfEngines():
    return PM(977091,978287)


def ConfEngines():
    return QtGui.QIcon(pmConfEngines())


def pmEngine():
    return PM(978287,979711)


def Engine():
    return QtGui.QIcon(pmEngine())


def pmZip():
    return PM(979711,980607)


def Zip():
    return QtGui.QIcon(pmZip())


def pmUpdate():
    return PM(980607,981691)


def Update():
    return QtGui.QIcon(pmUpdate())


def pmDGT():
    return PM(981691,982685)


def DGT():
    return QtGui.QIcon(pmDGT())


def pmDGTB():
    return PM(982685,983387)


def DGTB():
    return QtGui.QIcon(pmDGTB())


def pmMillenium():
    return PM(983387,984624)


def Millenium():
    return QtGui.QIcon(pmMillenium())


def pmCertabo():
    return PM(984624,985409)


def Certabo():
    return QtGui.QIcon(pmCertabo())


def pmNovag():
    return PM(985409,986276)


def Novag():
    return QtGui.QIcon(pmNovag())


def pmChessnut():
    return PM(986276,987051)


def Chessnut():
    return QtGui.QIcon(pmChessnut())


def pmSquareOff():
    return PM(987051,987807)


def SquareOff():
    return QtGui.QIcon(pmSquareOff())


def pmRodent():
    return PM(987807,988925)


def Rodent():
    return QtGui.QIcon(pmRodent())


def pmLeague():
    return PM(988925,990255)


def League():
    return QtGui.QIcon(pmLeague())


def pmJourney():
    return PM(990255,991494)


def Journey():
    return QtGui.QIcon(pmJourney())


def pmClassification():
    return PM(991494,992013)


def Classification():
    return QtGui.QIcon(pmClassification())


def pmNAGs():
    return PM(992013,992310)


def NAGs():
    return QtGui.QIcon(pmNAGs())


def pmSeason():
    return PM(992310,993108)


def Season():
    return QtGui.QIcon(pmSeason())


def pmNAG_0():
    return PM(993108,993329)


def NAG_0():
    return QtGui.QIcon(pmNAG_0())


def pmNAG_1():
    return PM(993329,993764)


def NAG_1():
    return QtGui.QIcon(pmNAG_1())


def pmNAG_2():
    return PM(993764,994321)


def NAG_2():
    return QtGui.QIcon(pmNAG_2())


def pmNAG_3():
    return PM(994321,995107)


def NAG_3():
    return QtGui.QIcon(pmNAG_3())


def pmNAG_4():
    return PM(995107,995918)


def NAG_4():
    return QtGui.QIcon(pmNAG_4())


def pmNAG_5():
    return PM(995918,996779)


def NAG_5():
    return QtGui.QIcon(pmNAG_5())


def pmNAG_6():
    return PM(996779,997559)


def NAG_6():
    return QtGui.QIcon(pmNAG_6())


def pmInformation():
    return PM(997559,1001039)


def Information():
    return QtGui.QIcon(pmInformation())


