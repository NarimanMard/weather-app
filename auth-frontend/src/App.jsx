import React, { useState } from 'react'

const AUTH_API = '/api/auth' 
function App() {
  const [isLogin, setIsLogin] = useState(true)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const handleAuth = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    const url = isLogin ? `${AUTH_API}/login` : `${AUTH_API}/register`
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
      })

      const data = await response.json()
      
      if (response.ok) {
        if (isLogin) {
          // Сохраняем данные и перенаправляем на weather app
          localStorage.setItem('username', data.username)
          localStorage.setItem('userId', data.userId)
          setMessage(`Добро пожаловать, ${data.username}! Перенаправляем...`)
          
          // Перенаправление на weather app через redirectUrl от бэкенда
          setTimeout(() => {
            window.location.href = data.redirectUrl || 'http://localhost:3000'
          }, 2000)
        } else {
          setMessage('Регистрация успешна! Теперь войдите.')
          setIsLogin(true)
          setUsername('')
          setPassword('')
        }
      } else {
        setMessage(data.message || 'Произошла ошибка')
      }
    } catch (error) {
      setMessage('Ошибка соединения с сервером')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>{isLogin ? 'Вход' : 'Регистрация'}</h1>
      
      <form onSubmit={handleAuth} className="auth-form">
        <input
          type="text"
          placeholder="Имя пользователя"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Загрузка...' : (isLogin ? 'Войти' : 'Зарегистрироваться')}
        </button>
      </form>

      {message && (
        <div className={`message ${message.includes('успеш') || message.includes('Добро') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      <button 
        className="switch-btn"
        onClick={() => {
          setIsLogin(!isLogin)
          setMessage('')
        }}
        type="button"
      >
        {isLogin ? 'Нет аккаунта? Зарегистрироваться' : 'Есть аккаунт? Войти'}
      </button>
    </div>
  )
}

export default App