interface BondCalculationsProps {
    nominalValue: number;
    quantity: number;
    initialInterestRate: number;
}

export default function BondCalculations({
    nominalValue,
    quantity,
    initialInterestRate,
}: BondCalculationsProps) {
    const totalValue = nominalValue * quantity;
    const annualIncome = (totalValue * initialInterestRate) / 100;

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
                        Годовой доход (ожидаемый)
                    </span>
                    <span className="font-bold text-green-600 text-lg">
                        {annualIncome.toLocaleString()} ₽
                    </span>
                </div>
            </div>
        </div>
    );
}
