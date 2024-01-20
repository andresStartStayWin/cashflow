from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

transacciones = []

def agregar_transacciones_recurrentes(hasta_fecha):
    transacciones_recurrentes = []
    fecha_actual = datetime.now()

    for transaccion in transacciones:
        if transaccion['frecuencia'] == 'única':
            continue

        fecha_inicio = transaccion['fecha']
        incremento = timedelta()

        if transaccion['frecuencia'] == 'diaria':
            incremento = timedelta(days=1)
        elif transaccion['frecuencia'] == 'semanal':
            incremento = timedelta(weeks=1)
        elif transaccion['frecuencia'] == 'mensual':
            incremento = timedelta(days=30)
        elif transaccion['frecuencia'] == 'anual':
            incremento = timedelta(days=365)

        if fecha_inicio <= fecha_actual:
            fecha_inicio += incremento

        while fecha_inicio <= hasta_fecha:
            transacciones_recurrentes.append({
                'tipo': transaccion['tipo'],
                'monto': transaccion['monto'],
                'fecha': fecha_inicio
            })
            fecha_inicio += incremento

    return transacciones_recurrentes

def calcular_sumatorias(periodo):
    suma = 0
    fecha_final = datetime.now() + timedelta(days=periodo)
    todas_transacciones = transacciones + agregar_transacciones_recurrentes(fecha_final)

    for transaccion in todas_transacciones:
        if transaccion['fecha'] <= fecha_final:
            suma += transaccion['monto']

    # Restar el monto de la primera ocurrencia de cada transacción recurrente
    montos_a_restar = 0
    for transaccion in transacciones:
        if transaccion['frecuencia'] != 'única' and transaccion['fecha'] <= fecha_final:
            montos_a_restar += transaccion['monto']

    suma -= montos_a_restar

    return suma

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        fecha_form = request.form['fecha']
        fecha_transaccion = datetime.strptime(fecha_form, '%Y-%m-%d') if fecha_form else datetime.now()

        transaccion = {
            'tipo': request.form['tipo'],
            'monto': float(request.form['monto']),
            'frecuencia': request.form['frecuencia'],
            'fecha': fecha_transaccion
        }
        transacciones.append(transaccion)
        return redirect(url_for('index'))

    sumatorias = {
        '7_dias': calcular_sumatorias(7),
        '1_mes': calcular_sumatorias(30),
        '3_meses': calcular_sumatorias(90),
        '6_meses': calcular_sumatorias(180),
        '9_meses': calcular_sumatorias(270),
        '1_año': calcular_sumatorias(365)
    }

    return render_template('index.html', transacciones=transacciones, sumatorias=sumatorias)

if __name__ == '__main__':
    app.run(debug=True)
