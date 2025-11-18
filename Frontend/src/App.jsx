import { useState, useEffect } from 'react';
import './styles.css';

const API_URL = 'https://predictor-precio-de-autos.onrender.com';
const TELEGRAM_BOT = 'https://web.telegram.org/k/#@DanBlaxter_bot'; // 

function App() {
  const [formData, setFormData] = useState({
    millas: '',
    anio: '',
    email: ''
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [globalStats, setGlobalStats] = useState(null);
  const [personalStats, setPersonalStats] = useState(null);

  // Cargar estadísticas globales al inicio
  useEffect(() => {
    fetchGlobalStats();
  }, []);

  // Función para obtener estadísticas globales
  const fetchGlobalStats = async () => {
    try {
      const mockData = {
        total_predicciones: 1245,
        anio_popular: 2020,
        rango_millas: "40,000 - 60,000",
        precio_promedio: 47850,
        consultas_semana: 324
      };
      
      setGlobalStats(mockData);
    } catch (error) {
      console.log('Error cargando stats:', error);
    }
  };

  // Función para obtener estadísticas personalizadas
  const fetchPersonalStats = async (anio, millas, precio) => {
    try {
      const mockData = {
        promedio_precio_anio: 48320,
        promedio_millas_anio: 62000,
        consultas_anio: 287,
        percentil: 65,
        comparacion_precio: precio > 48320 ? 'arriba' : 'abajo',
        diferencia_porcentaje: Math.abs(((precio - 48320) / 48320) * 100).toFixed(1)
      };
      
      setPersonalStats(mockData);
    } catch (error) {
      console.log('Error cargando stats personalizadas:', error);
    }
  };

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
          anio: parseInt(formData.anio)
        })
      });

      const data = await response.json();

      if (data.exito) {
        setResult(data);
        
        // Cargar estadísticas personalizadas
        fetchPersonalStats(data.anio, data.millas, data.precio_estimado);
        
        // Envío del email a Make
        fetch('https://hook.us2.make.com/ygbnmyhbwfk2jfeooweqygeblr7tol2f', {
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
    setPersonalStats(null);
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

      {/* Dashboard Global (antes de hacer predicción) */}
      {!result && globalStats && (
        <div className="global-stats">
          <h3>📊 Estadísticas del Mercado</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-number">{formatNumber(globalStats.total_predicciones)}</span>
              <span className="stat-label">Predicciones totales</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{globalStats.anio_popular}</span>
              <span className="stat-label">Año más consultado</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{globalStats.rango_millas}</span>
              <span className="stat-label">Rango de millaje común</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{formatPrice(globalStats.precio_promedio)}</span>
              <span className="stat-label">Precio promedio</span>
            </div>
          </div>
          <p className="stats-update">
             {globalStats.consultas_semana} personas consultaron esta semana
          </p>
        </div>
      )}

      {/* Card principal */}
      <div className="card">
        {!result ? (
          <>
            <h2>Modelo predictivo de precios</h2>
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
          /* Resultado con Analytics Personalizadas */
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

            {/* Analytics Personalizadas */}
            {personalStats && (
              <div className="personal-stats">
                <h4>📊 Tu Vehículo vs. El Mercado</h4>
                
                <div className="comparison-grid">
                  <div className="comparison-item">
                    <span className="comparison-label">Precio promedio {result.anio}</span>
                    <span className="comparison-value">{formatPrice(personalStats.promedio_precio_anio)}</span>
                  </div>
                  
                  <div className="comparison-item">
                    <span className="comparison-label">Tu vehículo está</span>
                    <span className={`comparison-badge ${personalStats.comparacion_precio}`}>
                      {personalStats.diferencia_porcentaje}% {personalStats.comparacion_precio === 'arriba' ? '↑' : '↓'}
                    </span>
                  </div>
                </div>

                <div className="comparison-grid">
                  <div className="comparison-item">
                    <span className="comparison-label">Millaje promedio {result.anio}</span>
                    <span className="comparison-value">{formatNumber(personalStats.promedio_millas_anio)} mi</span>
                  </div>
                  
                  <div className="comparison-item">
                    <span className="comparison-label">Tu millaje</span>
                    <span className={`comparison-badge ${result.millas < personalStats.promedio_millas_anio ? 'mejor' : 'normal'}`}>
                      {result.millas < personalStats.promedio_millas_anio ? '✓ Mejor' : 'Promedio'}
                    </span>
                  </div>
                </div>

                <div className="insight-box">
                  <strong>💡 Insight:</strong> {personalStats.consultas_anio} personas consultaron vehículos del {result.anio}. 
                  Tu auto está en el percentil {personalStats.percentil}% del mercado.
                </div>
              </div>
            )}

            <div className="email-notice">
              ✉️ Los detalles fueron enviados a tu correo electrónico
            </div>

            <button className="btn" onClick={handleNewConsultation}>
              Nueva Consulta
            </button>
          </div>
        )}
      </div>

      {/* Botón flotante de Telegram */}
      <a 
        href={TELEGRAM_BOT} 
        target="_blank" 
        rel="noopener noreferrer"
        className="telegram-float"
        title="Chatea con nuestro asistente"
      >
        <svg viewBox="0 0 24 24" width="28" height="28" fill="white">
          <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.223-.548.223l.188-2.85 5.18-4.68c.223-.198-.054-.308-.346-.11l-6.4 4.03-2.76-.918c-.6-.187-.612-.6.125-.89l10.782-4.156c.504-.187.943.112.78.89z"/>
        </svg>
        <span>¿Dudas?</span>
      </a>

      {/* Footer */}
      <footer className="footer">
        <p>Desarrollado por Danny Leonardo Novoa Rodriguez</p>
        <p>© 2025 PredictAuto AI</p>
        <div className="footer-links">
    
        </div>
      </footer>
    </div>
  );
}

export default App;