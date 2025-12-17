"use client";

import { useEffect, useState } from "react";
import { fetchWithAuth } from "@/lib/api";

interface BondCalculationsProps {
    bondHolderId: string;
    nominalValue: number;
    quantity: number;
    initialInterestRate: number;
}

export default function BondCalculations({
    bondHolderId,
    nominalValue,
    quantity,
    initialInterestRate,
}: BondCalculationsProps) {
    const [annualIncome, setAnnualIncome] = useState<number | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const totalValue = nominalValue * quantity;

    useEffect(() => {
        const fetchMonthlyIncome = async () => {
            setIsLoading(true);
            setError(null);

            try {
                const response = await fetchWithAuth(
                    `/calculations/month-income?bondholder_id=${bondHolderId}`,
                    {
                        method: "POST",
                    },
                );

                if (!response.ok) {
                    throw new Error("Не удалось получить данные о доходе");
                }

                const data = await response.json();
                console.log("Received data:", data);
                setAnnualIncome(Number(data));
            } catch (err) {
                setError(
                    err instanceof Error
                        ? err.message
                        : "Ошибка загрузки данных",
                );
                setAnnualIncome((totalValue * initialInterestRate) / 100);
            } finally {
                setIsLoading(false);
            }
        };

        fetchMonthlyIncome();
    }, [bondHolderId, totalValue, initialInterestRate]);

    return (
        <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Расчётные показатели
            </h3>
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg space-y-2">
                <div className="flex justify-between">
                    <span className="text-gray-600">
                        Общая стоимость портфеля
                    </span>
                    <span className="font-bold text-gray-900 text-lg">
                        {totalValue.toLocaleString()} ₽
                    </span>
                </div>

                <div className="flex justify-between">
                    <span className="text-gray-600">
                        Месячный доход (ожидаемый)
                    </span>
                    {isLoading ? (
                        <span className="font-bold text-gray-400 text-lg">
                            Загрузка...
                        </span>
                    ) : error ? (
                        <span
                            className="font-bold text-orange-600 text-lg"
                            title={error}
                        >
                            {annualIncome?.toLocaleString() || "—"} ₽
                        </span>
                    ) : (
                        <span className="font-bold text-green-600 text-lg">
                            {annualIncome?.toLocaleString() || "—"} ₽
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
