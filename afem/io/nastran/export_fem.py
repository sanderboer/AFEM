def export_bdf(assy, fn):
    """
    Export assembly of parts to Nastran bulk data format (only nodes and
    elements).
    """
    fout = open(fn, 'w')
    if not fout:
        return False

    fout.write("BEGIN BULK\n")

    # Dummy property for shells.
    fout.write("%-8s" % "PSHELL")
    # PID
    _write_field(1, fout)
    # MID
    _write_field(1, fout)
    # T
    _write_field(1., fout)
    fout.write('\n')

    # Write grids.
    for node in assy.nodes:
        fout.write("%-8s" % "GRID")
        # ID
        _write_field(node.nid, fout)
        # CP
        _write_field(None, fout)
        # X1
        _write_field(node.x, fout)
        # X2
        _write_field(node.y, fout)
        # X3
        _write_field(node.z, fout)
        # CD
        _write_field(None, fout)
        fout.write('\n')

    # Write elements.
    for elm in assy.elements:
        if elm.is_tri:
            fout.write("%-8s" % "CTRIA3")
        else:
            fout.write("%-8s" % "CQUAD4")
        # EID
        _write_field(elm.eid, fout)
        # PID
        _write_field(1, fout)
        for nid in elm.nids:
            _write_field(nid, fout)
        fout.write('\n')

    fout.write("ENDDATA")

    fout.close()


def _write_field(value, fout, fmt='small'):
    """
    Write data to Nastran bulk data file.
    """
    if fmt.lower() in ['small', 's']:
        small = True
    else:
        small = False

    # If None
    if value is None:
        if small:
            fout.write("        ")
            return True
        else:
            fout.write("                ")
            return True

    # Integer
    if isinstance(value, int):
        if small:
            fout.write("%8s" % str(value)[:8])
            return True
        else:
            fout.write("%16s" % str(value)[:16])
            return True

    # String
    if isinstance(value, str):
        if small:
            fout.write("%8s" % value[:8])
            return True
        else:
            fout.write("%16s" % value[:16])
            return True

    # Float
    if isinstance(value, float):
        # Get string representation of value
        str_val = str(value)
        # Get length of string representation
        len_value = len(str_val)

        # If the float has an exponent in it, split it there and then write
        # it depending on the format.
        exp = False
        for c in str_val:
            if c == 'e':
                exp = True
                break
        if exp:
            # Split string at "e"
            str_left, str_right = str_val.split('e')
            # Determine length of exponent
            len_exp = len(str_right)
            # Trim left string to fit based on format
            if small:
                if str_right[0] == '-':
                    str_left = str_left[:8 - len_exp]
                    str_out = str_left + str_right
                else:
                    str_left = str_left[:8 - (len_exp - 1)]
                    str_out = str_left + '+' + str_right
                fout.write("%8s" % str_out[:8])
            else:
                if str_right[0] == '-':
                    str_left = str_left[:16 - len_exp]
                    str_out = str_left + str_right
                else:
                    str_left = str_left[:16 - (len_exp - 1)]
                    str_out = str_left + '+' + str_right
                fout.write("%16s" % str_out[:16])
            return True

        # Small field format
        if small:
            # If string representation is less than 8, write it.
            if len_value <= 8:
                fout.write("%8s" % str_val)
                return True

            # If string representation is greater than 8,
            # split the string at the "." and convert to scientific
            # notation. Trim trailing digits to fit the exponent.

            # Split string at "."
            str_left, str_right = str_val.split('.')

            # If the left side is greater than or equal to 1 and the
            # first digit is not 0, convert to a "+" scientific notation.
            # Also, only use scientific notation if the length of the left
            # string is greater than 7.
            if len(str_left) >= 1 and str_left[0] != '0':
                if len(str_left) > 7:
                    exp = len(str_left) - 1
                    new_val = value / 10. ** exp
                    str_val = str(new_val)
                    # Export the string value making room for the exponent.
                    str_out = str_val[:7 - len(str(exp))] + "+" + str(exp)
                else:
                    str_out = str_val

                fout.write("%8s" % str_out[:8])
                return True

            # If the right side has more digits, convert to "-" scientific
            # notation only if the exponent is greater than 3.

            # Loop through the right string and find the first digit that
            # isn't 0.
            exp = 1
            for c in str_right:
                if int(c) == 0:
                    exp += 1
                else:
                    break

            # You only get an advantage from scientific notation if exp > 3.
            if exp > 3:
                new_val = value * 10. ** exp
                str_val = str(new_val)
                # Make room for the exponent.
                str_out = str_val[:7 - len(str(exp))] + "-" + str(exp)
            else:
                str_out = "." + str_right[:7]

            # Write to file
            fout.write("%8s" % str_out[:8])
            return True

        # Large field format
        # If string representation is less than 16, write it.
        if len_value <= 16:
            fout.write("%16s" % str_val)
            return True

        # If string representation is greater than 16,
        # split the string at the "." and convert to scientific
        # notation. Trim trailing digits to fit the exponent.

        # Split string at "."
        str_left, str_right = str_val.split('.')

        # If the left side is greater than or equal to 1 and the
        # first digit is not 0, convert to a "+" scientific notation.
        if len(str_left) >= 1 and str_left[0] != '0':
            exp = len(str_left) - 1
            new_val = value / 10. ** exp
            str_val = str(new_val)
            # Export the string value making room for the exponent.
            str_out = str_val[:15 - len(str(exp))] + "+" + str(exp)
            fout.write("%16s" % str_out[:16])
            return True

        # Loop through the right string and find the first digit that
        # isn't 0.
        exp = 1
        for c in str_right:
            if int(c) == 0:
                exp += 1
            else:
                break

        new_val = value * 10. ** exp
        str_val = str(new_val)
        # Make room for the exponent.
        str_out = str_val[:15 - len(str(exp))] + "-" + str(exp)

        # Write to file
        fout.write("%16s" % str_out[:16])
        return True