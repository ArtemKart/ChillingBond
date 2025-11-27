import Link from "next/link";

interface DashboardHeaderProps {
    onAddClick: () => void;
    onLogout: () => void;
}

export function DashboardHeader({
    onAddClick,
    onLogout,
}: DashboardHeaderProps) {
    return (
        <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-4">
                <Link
                    href="/"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                    Главная
                </Link>
                <h1 className="text-2xl font-bold text-gray-900">
                    Мои Облигации
                </h1>
            </div>
            <div className="flex gap-3">
                <button
                    onClick={onAddClick}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                    Добавить облигацию
                </button>
                <button
                    onClick={onLogout}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
                >
                    Выйти
                </button>
            </div>
        </div>
    );
}
