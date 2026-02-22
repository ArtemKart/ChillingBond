"use client";

import { useState } from "react";
import { calculateEstimatedMonthlyIncome } from "@/lib/bondCalculations";

interface BondCalculationsProps {
    bondHolderId: string;
    nominalValue: number;
    quantity: number;
    initialInterestRate: number;
    income: number | null;
}

export default function BondCalculations({
    nominalValue,
    quantity,
    initialInterestRate,
    income,
}: BondCalculationsProps) {
    const totalInvestment = nominalValue * quantity;
    const calculatedMonthlyAverage = calculateEstimatedMonthlyIncome(
        nominalValue,
        quantity,
        initialInterestRate,
    );
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
                        Expected month income
                    </p>

                    <div className="flex items-baseline gap-1">
                        <p className="text-xl font-bold text-green-900">
                            {income !== null
                                ? formatValue(income)
                                : formatValue(calculatedMonthlyAverage)}
                        </p>
                        <p className="text-xl font-bold text-green-900">PLN</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
