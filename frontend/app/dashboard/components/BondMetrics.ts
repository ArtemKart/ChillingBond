import { BondHolderResponse } from "@/types/Bond";

export interface BondMetrics {
    totalBondholders: number;
    totalInvestment: number;
    activeBonds: number;
    currentMonthIncome: number;
}

export function calculateBondMetrics(
    bonds: BondHolderResponse[],
    monthlyIncome?: number,
): BondMetrics {
    if (bonds.length === 0) {
        return {
            totalBondholders: 0,
            totalInvestment: 0,
            activeBonds: 0,
            currentMonthIncome: 0,
        };
    }

    const totalBondholders = bonds.length;

    const totalInvestment = bonds.reduce(
        (sum, bond) => sum + bond.nominal_value * bond.quantity,
        0,
    );

    const activeBonds = bonds.reduce((sum, bond) => sum + bond.quantity, 0);

    return {
        totalBondholders,
        totalInvestment,
        activeBonds,
        currentMonthIncome: monthlyIncome ?? 0,
    };
}

export function formatMetricValue(
    key: keyof BondMetrics,
    value: number,
): string {
    switch (key) {
        case "totalBondholders":
        case "activeBonds":
            return value.toString();
        case "totalInvestment":
            return `${value.toLocaleString()} PLN`;
        case "currentMonthIncome":
            return `${value.toLocaleString()} PLN`;
        default:
            return value.toString();
    }
}
