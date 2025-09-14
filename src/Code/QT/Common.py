def gb_style(points=16):
    return (
            """
        QGroupBox {
            font: bold %dpx;
            background-color: #F2F2EC;/*qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E0E0E0, stop: 1 #FFFFFF);*/
            border: 1px solid gray;
            border-radius: 3px;
            padding: 18px;
            margin-top: 15px; /* leave space at the top for the title */
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left; /* position at the top center */
            padding: 8px;
            margin-top: 2px;
            border: 1px solid gray;
         }
    """
            % points
    )


def gb_style_sub(points):
    return (
            """
        QGroupBox {
            font: bold %d;
            background-color: #F2F2EC;/*qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E0E0E0, stop: 1 #FFFFFF);*/
            border: 1px solid gray;
            border-radius: 3px;
            padding: 18px;
            margin-top: 5ex; /* leave space at the top for the title */
        }
        QGroupBox::title {
            subcontrol-position: top center; /* position at the top center */
            padding: 8px;
            border: 1px solid gray;
         }
    """
            % points
    )
