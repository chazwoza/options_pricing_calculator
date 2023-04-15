from flask import Flask, render_template, request
from scipy.stats import norm
import math

app = Flask(__name__)

def black_scholes_greeks(stock_price, strike_price, time_to_expiration, risk_free_rate, implied_volatility, option_type):
    d1 = (math.log(stock_price / strike_price) + (risk_free_rate + 0.5 * implied_volatility ** 2) * time_to_expiration) / (implied_volatility * math.sqrt(time_to_expiration))
    d2 = d1 - implied_volatility * math.sqrt(time_to_expiration)
    phi_d1 = norm.pdf(d1)

    if option_type.lower() == 'call':
        price = stock_price * norm.cdf(d1) - strike_price * math.exp(-risk_free_rate * time_to_expiration) * norm.cdf(d2)
        delta = norm.cdf(d1)
    elif option_type.lower() == 'put':
        price = strike_price * math.exp(-risk_free_rate * time_to_expiration) * norm.cdf(-d2) - stock_price * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
    else:
        raise ValueError('Invalid option type. Use "call" or "put".')

    gamma = phi_d1 / (stock_price * implied_volatility * math.sqrt(time_to_expiration))
    vega = stock_price * phi_d1 * math.sqrt(time_to_expiration) / 100
    theta = -(stock_price * phi_d1 * implied_volatility / (2 * math.sqrt(time_to_expiration)) + risk_free_rate * strike_price * math.exp(-risk_free_rate * time_to_expiration) * norm.cdf(d2)) / 365
    rho = strike_price * time_to_expiration * math.exp(-risk_free_rate * time_to_expiration) * norm.cdf(d2) / 100

    return price, delta, gamma, vega, theta, rho

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock_price = float(request.form['stock_price'])
        strike_price = float(request.form['strike_price'])
        time_to_expiration = float(request.form['time_to_expiration'])
        risk_free_rate = float(request.form['risk_free_rate'])
        implied_volatility = float(request.form['implied_volatility'])
        option_type = request.form['option_type']

        option_price, delta, gamma, vega, theta, rho = black_scholes_greeks(stock_price, strike_price, time_to_expiration / 365, risk_free_rate / 100, implied_volatility / 100, option_type)
        return render_template('index.html', option_price=option_price, delta=delta, gamma=gamma, vega=vega, theta=theta, rho=rho, stock_price=stock_price, strike_price=strike_price, time_to_expiration=time_to_expiration, risk_free_rate=risk_free_rate, implied_volatility=implied_volatility, option_type=option_type)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
