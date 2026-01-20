interface BondFinancialParamsProps {
    nominalValue: number;
    initialInterestRate: number;
    referenceRateMargin: number;
    firstInterestPeriod: number;
    isEditing: boolean;
    onChange: (field: string, value: number) => void;
}

export default function BondFinancialParams({
    nominalValue,
    initialInterestRate,
    referenceRateMargin,
    firstInterestPeriod,
    isEditing,
    onChange,
}: BondFinancialParamsProps) {
    return (
        <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Financial Parameters
            </h3>
            <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">Face value</span>
                    {isEditing ? (
                        <input
                            type="number"
                            step="0.01"
                            value={nominalValue}
                            onChange={(e) =>
                                onChange(
                                    "nominal_value",
                                    parseFloat(e.target.value),
                                )
                            }
                            className="font-semibold text-gray-900 w-32 bg-white border border-gray-300 rounded px-2 py-1 text-right"
                        />
                    ) : (
                        <span className="font-semibold text-gray-900">
                            {nominalValue.toLocaleString()} PLN
                        </span>
                    )}
                </div>

                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">
                        Initial Interest Rate
                    </span>
                    {isEditing ? (
                        <div className="flex items-center gap-1">
                            <input
                                type="number"
                                step="0.01"
                                value={initialInterestRate}
                                onChange={(e) =>
                                    onChange(
                                        "initial_interest_rate",
                                        parseFloat(e.target.value),
                                    )
                                }
                                className="font-semibold text-green-600 w-24 bg-white border border-gray-300 rounded px-2 py-1 text-right"
                            />
                            <span className="font-semibold text-green-600">
                                %
                            </span>
                        </div>
                    ) : (
                        <span className="font-semibold text-green-600">
                            {initialInterestRate}%
                        </span>
                    )}
                </div>

                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">Rate Margin</span>
                    {isEditing ? (
                        <div className="flex items-center gap-1">
                            <input
                                type="number"
                                step="0.01"
                                value={referenceRateMargin}
                                onChange={(e) =>
                                    onChange(
                                        "reference_rate_margin",
                                        parseFloat(e.target.value),
                                    )
                                }
                                className="font-semibold text-gray-900 w-24 bg-white border border-gray-300 rounded px-2 py-1 text-right"
                            />
                            <span className="font-semibold text-gray-900">
                                %
                            </span>
                        </div>
                    ) : (
                        <span className="font-semibold text-gray-900">
                            {referenceRateMargin > 0 ? "+" : ""}
                            {referenceRateMargin}%
                        </span>
                    )}
                </div>

                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">
                        First Interest Period
                    </span>
                    {isEditing ? (
                        <div className="flex items-center gap-1">
                            <input
                                type="number"
                                value={firstInterestPeriod}
                                onChange={(e) =>
                                    onChange(
                                        "first_interest_period",
                                        parseInt(e.target.value),
                                    )
                                }
                                className="font-semibold text-gray-900 w-24 bg-white border border-gray-300 rounded px-2 py-1 text-right"
                            />
                            <span className="font-semibold text-gray-900">
                                pcs
                            </span>
                        </div>
                    ) : (
                        <span className="font-semibold text-gray-900">
                            {firstInterestPeriod} pcs
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
