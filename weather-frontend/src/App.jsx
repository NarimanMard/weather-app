import React, { useState, useEffect } from 'react'

const WEATHER_API = '/api/weather'

function App() {
  const [city, setCity] = useState('Moscow')
  const [country, setCountry] = useState('ru')
  const [weatherData, setWeatherData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [user, setUser] = useState(null)

  useEffect(() => {
    // Получаем пользователя из URL параметра (после редиректа с auth)
    const urlParams = new URLSearchParams(window.location.search)
    const urlUser = urlParams.get('user')
    
    if (urlUser) {
      setUser(urlUser)
      localStorage.setItem('username', urlUser)
      loadWeather() // Автоматически загружаем погоду
    } else {
      // Проверяем localStorage
      const savedUser = localStorage.getItem('username')
      if (savedUser) {
        setUser(savedUser)
        loadWeather()
      } else {
        // Если не авторизован - перенаправляем на auth
        window.location.href = 'http://localhost:3001'
      }
    }
  }, [])

  const loadWeather = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await fetch(`${WEATHER_API}/${city},${country}`)
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      setWeatherData(data)
    } catch (err) {
      setError(`Ошибка: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('username')
    window.location.href = 'http://localhost:3001'
  }

  if (!user) {
    return <div className="loading">Проверка авторизации...</div>
  }

  return (
    <div className="container">
      <div className="header">
        <h1>🌤️ Погода</h1>
        <div className="user-info">
          <span>Привет, {user}!</span>
          <button onClick={logout} className="logout-btn">Выйти</button>
        </div>
      </div>

      <div className="weather-controls">
        <input
          type="text"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          placeholder="Город"
        />
        <input
          type="text"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          placeholder="Код страны (ru, us, it)"
          maxLength="2"
        />
        <button onClick={loadWeather} disabled={loading}>
          {loading ? 'Загрузка...' : 'Узнать погоду'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {weatherData && (
        <div className="weather-card ">
          <h2>{weatherData.city}, {weatherData.country}</h2>
          <div className="weather-main">
            <div className="temperature increase">
              {weatherData.temperature}°C
            </div>
            <div className="description ">
              {weatherData.description}
            </div>
          </div>
          <div className="weather-details">
            <div className="detail increase">
              <span>💧Твоя Влажность😉</span>
              <span>{weatherData.humidity}%</span>
            </div>
            <div className="detail increase">
              <span>💨 Ветер</span>
              <span>{weatherData.windSpeed} м/с</span>
            </div>
            <div className="detail increase">
              <span>🎯 Давление</span>
              <span>{weatherData.pressure} hPa</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App