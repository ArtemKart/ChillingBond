interface BondFinancialParamsProps {
    nominalValue: number;
    initialInterestRate: number;
    referenceRateMargin: number;
    firstInterestPeriod: number;
}

export default function BondFinancialParams({
    nominalValue,
    initialInterestRate,
    referenceRateMargin,
    firstInterestPeriod,
}: BondFinancialParamsProps) {
    return (
        <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Financial Parameters
            </h3>
            <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">Face value</span>
                    <span className="font-semibold text-gray-900">
                        {nominalValue.toLocaleString()} PLN
                    </span>
                </div>

                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">Initial Interest Rate</span>
                    <span className="font-semibold text-green-600">
                        {initialInterestRate}%
                    </span>
                </div>

                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">Rate Margin</span>
                    <span className="font-semibold text-gray-900">
                        {referenceRateMargin}%
                    </span>
                </div>

                <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">First Interest Period</span>
                    <span className="font-semibold text-gray-900">
                        {firstInterestPeriod} pcs
                    </span>
                </div>
            </div>
        </div>
    );
}
