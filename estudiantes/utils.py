def validar_cedula(cedula):
    # Verificar que la cédula tenga 10 dígitos
    if len(cedula) != 10:
        return False
    try:
        # Convertir a enteros para asegurarse de que la cédula sea numérica
        int(cedula)
    except ValueError:
        return False
    # Los dos primeros dígitos corresponden al código de la provincia
    provincia = int(cedula[0:2])
    if provincia < 1 or provincia > 24:
        return False
    # El tercer dígito debe estar entre 0 y 6 para una cédula válida
    if int(cedula[2]) >= 6:
        return False
    # Algoritmo de validación de la cédula
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    for i in range(9):
        valor = int(cedula[i]) * coeficientes[i]
        if valor >= 10:
            valor -= 9
        suma += valor
    # Obtener el dígito verificador
    digito_verificador = 10 - (suma % 10)
    if digito_verificador == 10:
        digito_verificador = 0
    # Comparar el dígito verificador calculado con el último dígito de la cédula
    return digito_verificador == int(cedula[9])


def validar_ruc(ruc):
    # Verificar que el RUC tenga 13 dígitos
    if len(ruc) != 13:
        return False
    
    # Verificar que los últimos tres dígitos sean numéricos (generalmente '001')
    if not ruc[-3:].isdigit():
        return False

    # Obtener los primeros 10 dígitos (que corresponden a la cédula)
    cedula = ruc[:10]

    # Verificar que la cédula tenga 10 dígitos
    if len(cedula) != 10:
        return False
    try:
        # Convertir a enteros para asegurarse de que la cédula sea numérica
        int(cedula)
    except ValueError:
        return False
    # Los dos primeros dígitos corresponden al código de la provincia
    provincia = int(cedula[0:2])
    if provincia < 1 or provincia > 24:
        return False
    # El tercer dígito debe estar entre 0 y 6 para una cédula válida
    if int(cedula[2]) >= 6:
        return False
    # Algoritmo de validación de la cédula (primeros 9 dígitos del RUC)
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    for i in range(9):
        valor = int(cedula[i]) * coeficientes[i]
        if valor >= 10:
            valor -= 9
        suma += valor
    # Obtener el dígito verificador
    digito_verificador = 10 - (suma % 10)
    if digito_verificador == 10:
        digito_verificador = 0
    # Comparar el dígito verificador calculado con el décimo dígito del RUC
    return digito_verificador == int(cedula[9])
