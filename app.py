import math
from flask import Flask, request, jsonify, make_response, render_template
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def impresion_json():
    if request.method == 'POST':
        # Datos para la FFT
        datos = [1, 10, 3, 8, 5]  # Ejemplo de datos con mayor variación
        # Ejemplo de datos, puedes modificarlos según tus necesidades
        # Obtener datos de la solicitud
        # data = request.get_json()
        # datos = data['data']

        # Realizar cálculos de FFT
        complejos = [complejo(num, 0) for num in datos]
        resultado = Calc_fft(complejos)

        # Generar gráfico
        freqs = range(len(resultado))
        magnitudes = [mag(complex_num) for complex_num in resultado]
        fases = [fase(complex_num) for complex_num in resultado]

        fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(12, 10))
        fig.subplots_adjust(hspace=0.5)

        ax1.plot(freqs, magnitudes)
        ax1.set_xlabel('Frecuencia')
        ax1.set_ylabel('Magnitud')
        ax1.set_title('Gráfico de Magnitud FFT')

        ax2.plot(freqs, fases)
        ax2.set_xlabel('Frecuencia')
        ax2.set_ylabel('Fase')
        ax2.set_title('Gráfico de Fase FFT')

        # Guardar gráfico en un objeto BytesIO
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Convertir gráfico a base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Generar respuesta JSON
        json_result = {
            'fft': [
                {
                    'freq': freq,
                    'mag': mag_value,
                    'phase': phase_value
                }
                for freq, mag_value, phase_value in zip(freqs, magnitudes, fases)
            ],
            'image': image_base64
        }

        # Configurar encabezados de respuesta
        headers = {'Content-Type': 'application/json'}

        # Enviar respuesta
        return make_response(jsonify(json_result), 200, headers)

    return render_template('index.html')


class complejo:
    # Atributos
    def __init__(self, real, imaginario):
        self.re = real
        self.im = imaginario


def Calc_fft(vector):
    n = len(vector)

    if n <= 1:
        return vector

    lstImpar = []
    lstPar = []

    for i in range(n):
        if i % 2 == 0:
            lstPar.append(vector[i])
        else:
            lstImpar.append(vector[i])

    lstPar = Calc_fft(lstPar)
    lstImpar = Calc_fft(lstImpar)

    resultado = []

    for m in range(n // 2):
        w = complejo(math.cos(2 * math.pi * m / n), -math.sin(2 * math.pi * m / n))
        z = complejo((w.re * lstImpar[m].re) - (w.im * lstImpar[m].im),
                     (w.re * lstImpar[m].im) + (w.im * lstImpar[m].re))

        resultado.append(complejo(lstPar[m].re + z.re, lstPar[m].im + z.im))
        resultado.append(complejo(lstPar[m].re - z.re, lstPar[m].im - z.im))

    return resultado


def mag(complejo):
    Mag = math.sqrt(math.pow(complejo.re, 2) + math.pow(complejo.im, 2))
    return Mag


def fase(complejo):
    if complejo.re != 0:
        Fase = (math.atan(complejo.im / complejo.re) * 180 / math.pi)
    else:
        Fase = 0
    return Fase


if __name__ == '__main__':
    app.run()
