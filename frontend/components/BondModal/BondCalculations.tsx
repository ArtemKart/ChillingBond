"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

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
    const [income, setIncome] = useState<number | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchMonthlyIncome = async () => {
            try {
                // The API currently returns a single number (Decimal) representing income
                const result = await apiFetch<number>(
                    `/calculations/month-income?bondholder_id=${bondHolderId}`,
                    {
                        method: "POST",
                    },
                );
                setIncome(result);
            } catch (err) {
                setError(
                    err instanceof Error
                        ? err.message
                        : "Не удалось получить данные о доходе",
                );
            } finally {
                setLoading(false);
            }
        };

        fetchMonthlyIncome();
    }, [bondHolderId]);

    const totalInvestment = nominalValue * quantity;
    // Fallback calculation if API fails or is loading
    const calculatedMonthlyAverage =
        (totalInvestment * (initialInterestRate / 100)) / 12;

    const formatValue = (val: number) => {
        return val.toLocaleString("ru-RU", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    };

    return (
        <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">
                Yield Calculation
            </h3>

            <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-blue-50 rounded-lg">
                    <p className="text-xs text-blue-600 font-medium uppercase">
                        Total Face Value
                    </p>
                    <p className="text-xl font-bold text-blue-900">
                        {totalInvestment.toLocaleString("ru-RU")} PLN
                    </p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                    <p className="text-xs text-green-600 font-medium uppercase">
                        Monthly Income
                    </p>
                    <div className="flex items-baseline gap-1">
                        <p className="text-xl font-bold text-green-900">
                            {loading ? (
                                <span className="animate-pulse">...</span>
                            ) : income !== null ? (
                                formatValue(income)
                            ) : (
                                formatValue(calculatedMonthlyAverage)
                            )}
                        </p>
                        <p className="text-xl font-bold text-green-900">PLN</p>
                    </div>
                </div>
            </div>

            {error && (
                <div className="text-amber-600 text-xs bg-amber-50 p-2 rounded border border-amber-100">
                    Due to service error, the calculation is based on the initial interest rate.
                </div>
            )}
        </div>
    );
}
