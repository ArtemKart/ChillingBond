import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link href="/" className="text-2xl font-bold text-blue-600">
                ChillingBond
              </Link>
            </div>

            {/* Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link href="/" className="text-gray-700 hover:text-blue-600 font-medium">
                Главная
              </Link>
              <Link href="/dashboard" className="text-gray-700 hover:text-blue-600 font-medium">
                Дашборд
              </Link>
              <Link href="/about" className="text-gray-700 hover:text-blue-600 font-medium">
                О проекте
              </Link>
            </div>

            {/* Auth buttons */}
            <div className="flex items-center space-x-4">
              <Link
                href="/login"
                className="text-gray-700 hover:text-blue-600 font-medium"
              >
                Войти
              </Link>
              <Link
                href="/register"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition font-medium"
              >
                Регистрация
              </Link>
            </div>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Управляйте своим портфелем
            <span className="text-blue-600"> облигаций</span> в одном месте
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Отслеживайте доходность, анализируйте инвестиции и получайте уведомления
            о выплатах купонов. Всё что нужно для эффективного управления облигациями.
          </p>
          <div className="flex justify-center gap-4">
            <Link
              href="/register"
              className="bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition text-lg font-semibold shadow-lg"
            >
              Начать бесплатно
            </Link>
            <Link
              href="/dashboard"
              className="bg-white text-blue-600 px-8 py-4 rounded-lg hover:bg-gray-50 transition text-lg font-semibold border-2 border-blue-600"
            >
              Перейти к дашборду
            </Link>
          </div>
        </div>

        {/* Visual placeholder - можно добавить график или иллюстрацию */}
        <div className="mt-16 bg-white rounded-xl shadow-2xl p-8 border border-gray-200">
          <div className="aspect-video bg-gradient-to-br from-blue-100 to-blue-50 rounded-lg flex items-center justify-center">
            <p className="text-gray-500 text-lg">📊 Визуализация портфеля</p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            Ключевые возможности
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Feature 1 */}
            <div className="bg-blue-50 rounded-xl p-6 hover:shadow-lg transition">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">📈</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Отслеживание облигаций
              </h3>
              <p className="text-gray-600">
                Добавляйте облигации в портфель и следите за их текущей стоимостью в режиме реального времени
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-green-50 rounded-xl p-6 hover:shadow-lg transition">
              <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">💰</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Анализ доходности
              </h3>
              <p className="text-gray-600">
                Рассчитывайте текущую доходность, прогнозируйте будущие выплаты и оптимизируйте портфель
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-purple-50 rounded-xl p-6 hover:shadow-lg transition">
              <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">📝</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                История операций
              </h3>
              <p className="text-gray-600">
                Ведите полную историю покупок, продаж и получения купонов для налоговой отчётности
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-orange-50 rounded-xl p-6 hover:shadow-lg transition">
              <div className="w-12 h-12 bg-orange-600 rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">🔔</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Уведомления о выплатах
              </h3>
              <p className="text-gray-600">
                Получайте напоминания о предстоящих выплатах купонов и погашении облигаций
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How it works Section */}
      <section className="py-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            Как это работает
          </h2>

          <div className="space-y-12">
            {/* Step 1 */}
            <div className="flex items-start gap-6">
              <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center text-xl font-bold">
                1
              </div>
              <div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                  Регистрация
                </h3>
                <p className="text-gray-600 text-lg">
                  Создайте бесплатный аккаунт за 30 секунд. Никаких сложных форм или проверок.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex items-start gap-6">
              <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center text-xl font-bold">
                2
              </div>
              <div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                  Добавление облигаций
                </h3>
                <p className="text-gray-600 text-lg">
                  Внесите информацию о своих облигациях: серия, количество, дата покупки. Система автоматически рассчитает все показатели.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex items-start gap-6">
              <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center text-xl font-bold">
                3
              </div>
              <div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                  Отслеживание портфеля
                </h3>
                <p className="text-gray-600 text-lg">
                  Следите за доходностью, получайте аналитику и уведомления. Всё необходимое для успешных инвестиций в одном месте.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-12 text-center">
            <Link
              href="/register"
              className="inline-block bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition text-lg font-semibold"
            >
              Попробовать сейчас →
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            {/* Column 1 */}
            <div>
              <h3 className="text-xl font-bold mb-4">ChillingBond</h3>
              <p className="text-gray-400">
                Современный инструмент для управления портфелем облигаций
              </p>
            </div>

            {/* Column 2 */}
            <div>
              <h4 className="font-semibold mb-4">Ссылки</h4>
              <ul className="space-y-2">
                <li>
                  <Link href="/" className="text-gray-400 hover:text-white">
                    Главная
                  </Link>
                </li>
                <li>
                  <Link href="/dashboard" className="text-gray-400 hover:text-white">
                    Дашборд
                  </Link>
                </li>
                <li>
                  <Link href="/about" className="text-gray-400 hover:text-white">
                    О проекте
                  </Link>
                </li>
              </ul>
            </div>

            {/* Column 3 */}
            <div>
              <h4 className="font-semibold mb-4">Контакты</h4>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a href="mailto:info@chillingbond.com" className="hover:text-white">
                    info@chillingbond.com
                  </a>
                </li>
                <li>
                  <Link href="/privacy" className="hover:text-white">
                    Политика конфиденциальности
                  </Link>
                </li>
                <li className="flex gap-4 mt-4">
                  <a href="#" className="hover:text-white">Telegram</a>
                  <a href="#" className="hover:text-white">GitHub</a>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 ChillingBond. Все права защищены.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
