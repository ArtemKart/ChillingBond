'use client';

import { useEffect, useState } from 'react';
import { fetchWithAuth } from '@/lib/api';
import type { BondHolderResponse } from '@/types/bond';
import BondModal from '@/components/BondModal';
import AddBondModal from '@/components/AddBondModal';
import Link from "next/link";

export default function Dashboard() {
  const [bonds, setBonds] = useState<BondHolderResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedBond, setSelectedBond] = useState<BondHolderResponse | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const groupedBonds = bonds.reduce((acc, bond) => {
      const dateKey = new Date(bond.purchase_date).toLocaleDateString('ru-RU');
      if (!acc[dateKey]) {
        acc[dateKey] = [];
      }
      acc[dateKey].push(bond);
      return acc;
  }, {} as Record<string, BondHolderResponse[]>);

  const loadBonds = async () => {
    try {
      const response = await fetchWithAuth('/bonds');

      if (!response.ok) {
        throw new Error('Не удалось загрузить облигации');
      }

      const result = await response.json();
      setBonds(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBonds();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('token_type');
    window.location.href = '/login';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-600">Загрузка...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

   return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
          <Link
              href="/"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Главная
            </Link>
        <h1 className="text-2xl font-bold text-gray-900">Мои Облигации</h1>
        <div className="flex gap-3">
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Добавить облигацию
          </button>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
          >
            Выйти
          </button>
        </div>
      </div>

      {/* Bonds List */}
      <div className="bg-white rounded-lg shadow">
        {bonds.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            У вас пока нет облигаций
          </div>
        ) : (
          <div>
            {Object.entries(groupedBonds).map(([date, dateBonds]) => (
              <div key={date}>
                <div className="px-6 py-3 bg-gray-100 text-sm font-medium text-gray-700 border-b border-gray-200">
                  Куплено {date}
                </div>
                <ul className="divide-y divide-gray-200">
                  {dateBonds.map((bond) => (
                    <li
                      key={bond.id}
                      className="p-6 hover:bg-gray-50 transition cursor-pointer"
                      onClick={() => setSelectedBond(bond)}
                    >
                      <div className="flex justify-between items-center">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">
                              Серия {bond.series}
                            </h3>
                            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full font-semibold">
                              {bond.quantity} шт.
                            </span>
                          </div>

                          <div className="flex gap-6 text-sm text-gray-600">
                            <div>
                              <span className="font-medium">Номинал:</span>{' '}
                              {bond.nominal_value.toLocaleString()} ₽
                            </div>
                            <div>
                              <span className="font-medium">Ставка:</span>{' '}
                              {bond.initial_interest_rate}%
                            </div>
                            <div>
                              <span className="font-medium">Куплено:</span>{' '}
                              {new Date(bond.purchase_date).toLocaleDateString('ru-RU')}
                            </div>
                          </div>
                        </div>

                        <div className="ml-4">
                          <span className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                            Подробнее →
                          </span>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      {selectedBond && (
        <BondModal
          bond={selectedBond}
          onClose={() => setSelectedBond(null)}
          onUpdate={loadBonds}
        />
      )}
      {/* Add Modal */}
      {isAddModalOpen && (
        <AddBondModal
          onClose={() => setIsAddModalOpen(false)}
          onUpdate={loadBonds}
        />
      )}
    </div>
  );
}
