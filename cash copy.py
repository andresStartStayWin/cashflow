from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

transacciones = []

def agregar_transacciones_recurrentes(hasta_fecha):
    transacciones_recurrentes = []
    fecha_actual = datetime.now()

    for transaccion in transacciones:
        if transaccion['frecuencia'] == 'única':
            continue  # Excluir transacciones únicas

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

        # Avanzar la fecha_inicio si la transacción comienza hoy o en el pasado
        if fecha_inicio <= fecha_actual:
            fecha_inicio += incremento

        # Agregar las ocurrencias recurrentes hasta la fecha límite
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
        '7_dias': calcular_sumatorias(6),
        '1_mes': calcular_sumatorias(29),
        '3_meses': calcular_sumatorias(89),
        '6_meses': calcular_sumatorias(179),
        '9_meses': calcular_sumatorias(269),
        '1_año': calcular_sumatorias(364)
    }

    return render_template('index.html', transacciones=transacciones, sumatorias=sumatorias)

if __name__ == '__main__':
    app.run(debug=True)
