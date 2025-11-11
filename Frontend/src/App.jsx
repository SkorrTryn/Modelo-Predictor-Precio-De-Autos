import { useState } from 'react';
import './styles.css';

const API_URL = 'https://predictor-precio-de-autos.onrender.com';

function App() {
  const [formData, setFormData] = useState({
    millas: '',
    anio: '',
    email: ''
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  // Validar campos
  const validateField = (name, value) => {
    const newErrors = { ...errors };

    if (name === 'millas') {
      if (value && (value < 0 || value > 500000)) {
        newErrors.millas = '❌ El millaje debe estar entre 0 y 500,000';
      } else {
        delete newErrors.millas;
      }
    }

    if (name === 'anio') {
      if (value && (value < 2000 || value > 2030)) {
        newErrors.anio = '❌ El año debe estar entre 2000 y 2030';
      } else {
        delete newErrors.anio;
      }
    }

    if (name === 'email') {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (value && !emailRegex.test(value)) {
        newErrors.email = '❌ Email no válido';
      } else {
        delete newErrors.email;
      }
    }

    setErrors(newErrors);
  };

  // Manejar cambios en inputs
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    validateField(name, value);
  };

  // Enviar formulario
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.millas || !formData.anio || !formData.email) {
      alert('Por favor completa todos los campos');
      return;
    }

    if (Object.keys(errors).length > 0) {
      alert('Por favor corrige los errores');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/predecir`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          millas: parseFloat(formData.millas),
          anio: parseInt(formData.anio),
          email: formData.email
        })
      });

      const data = await response.json();

     if (data.exito) {
  setResult(data);
  
  // Envio del email a n8n
  fetch('https://novoanevn.app.n8n.cloud/webhook/predictauto', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: formData.email,
      millas: data.millas,
      anio: data.anio,
      precio: data.precio_estimado
    })
  }).catch(err => {
    
    console.log('Email notification error:', err);
  });
} else {
  alert('Error al calcular el precio');
}
    } catch (error) {
      console.error('Error:', error);
      alert('Error al conectar con el servidor');
    } finally {
      setLoading(false);
    }
  };

  // Nueva consulta
  const handleNewConsultation = () => {
    setFormData({ millas: '', anio: '', email: '' });
    setErrors({});
    setResult(null);
  };

  // Formatear precio
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(price);
  };

  // Formatear número
  const formatNumber = (num) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const isFormValid = formData.millas && formData.anio && formData.email && Object.keys(errors).length === 0;

  return (
    <div className="container">
      {/* Header */}
    <header className="header">
  <h1>PredictAuto AI</h1>
  <img 
    src="/iconocoche.png" 
    alt="Carro" 
    style={{ 
      width: '80px', 
      height: '80px', 
      marginTop: '1px',
      marginBottom: '1px'
    }} 
  />
  <p>Descubre el valor real de tu vehículo</p>
</header>

      {/* Card principal */}
      <div className="card">
        {!result ? (
          <>
            <h2>Modelo predectivo de precios</h2>
             {/* Información del modelo */}
                <div style={{
                display: 'flex',
                justifyContent: 'center',
                gap: '25px',
                marginBottom: '30px',
                fontSize: '13px',
                color: '#888',
                flexWrap: 'wrap'
                }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ 
                    width: '8px', 
                    height: '8px', 
                    backgroundColor: '#468B62', 
                    borderRadius: '50%',
                    display: 'inline-block'
                    }}></span>
                    <span>3,943 vehículos analizados</span>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ 
                    width: '8px', 
                    height: '8px', 
                    backgroundColor: '#BC605C', 
                    borderRadius: '50%',
                    display: 'inline-block'
                    }}></span>
                    <span>Precisión promedio: ±$27,826</span>
                </div>
                </div>
            
            

            

            <form onSubmit={handleSubmit}>
              {/* Millaje */}
              <div className="form-group">
                <label htmlFor="millas">Millaje (millas)</label>
                <input
                  type="number"
                  id="millas"
                  name="millas"
                  value={formData.millas}
                  onChange={handleChange}
                  placeholder="Ej: 50000"
                  min="0"
                  max="500000"
                />
                {errors.millas && (
                  <span className="error-message">{errors.millas}</span>
                )}
              </div>

              {/* Año */}
              <div className="form-group">
                <label htmlFor="anio">Año del modelo</label>
                <input
                  type="number"
                  id="anio"
                  name="anio"
                  value={formData.anio}
                  onChange={handleChange}
                  placeholder="Ej: 2020"
                  min="2000"
                  max="2030"
                />
                {errors.anio && (
                  <span className="error-message">{errors.anio}</span>
                )}
              </div>

              {/* Email */}
              <div className="form-group">
                <label htmlFor="email">Tu correo electrónico</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="tu@email.com"
                />
                {errors.email && (
                  <span className="error-message">{errors.email}</span>
                )}
              </div>

              {/* Botón */}
              <button 
                type="submit" 
                className="btn" 
                disabled={!isFormValid || loading}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Calculando...
                  </>
                ) : (
                  'Calcular Precio'
                )}
              </button>
            </form>
          </>
        ) : (
          /* Resultado */
          <div className="result">
            <div className="result-icon">✓</div>
            <h3>Precio Calculado</h3>
            
            <div className="result-price">
              {formatPrice(result.precio_estimado)}
            </div>

            <div className="result-details">
              <div className="result-row">
                <span className="result-label">Millaje:</span>
                <span className="result-value">{formatNumber(result.millas)} millas</span>
              </div>
              <div className="result-row">
                <span className="result-label">Año:</span>
                <span className="result-value">{result.anio}</span>
              </div>
              <div className="result-row">
                <span className="result-label">Estado:</span>
                <span className="result-value">{result.mensaje}</span>
              </div>
            </div>

            <div className="email-notice">
              Los detalles fueron enviados a tu correo electrónico
            </div>

            <button className="btn" onClick={handleNewConsultation}>
              Nueva Consulta
            </button>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>Desarrollado por Danny Leonardo Novoa Rodriguez</p>
        <p>© 2025 PredictAuto AI</p>
      </footer>
    </div>
  );
}

export default App;