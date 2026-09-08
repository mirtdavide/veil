import { useState } from 'react'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import Mainshell from './pages/Mainshell'

type View = 'login' | 'register' | 'shell'

function App(): React.JSX.Element {
  const [view, setView] = useState<View>('login')

  function handleLogin(email: string, password: string): void {
    console.log('login da App', email, password)
    setView('shell') // Switch to the main shell view after successful login
  }

  function handleRegister(
    username: string,
    email: string,
    password: string,
    inviteCode: string
  ): void {
    console.log('register da App', username, email, password, inviteCode)
    setView('login') // Switch to the login view after successful registration
  }

  if (view === 'login') {
    return <LoginPage onLogin={handleLogin} onNavigateToRegister={() => setView('register')} />
  }

  if (view === 'register') {
    return <RegisterPage onRegister={handleRegister} onNavigateToLogin={() => setView('login')} />
  }


  return <Mainshell />
}

export default App