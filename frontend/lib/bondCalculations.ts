import { apiFetch } from "./api";

export async function fetchMonthlyIncome(
    targetDate?: string,
): Promise<Record<string, number>> {
    let dateToUse = targetDate;

    if (!dateToUse) {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, "0");
        dateToUse = `${year}-${month}-01`;
    }

    const response = await apiFetch<{ data: Record<string, string> }>(
        `/calculations/month-income?target_date=${dateToUse}`,
        { method: "POST" },
    );
    return Object.fromEntries(
        Object.entries(response.data).map(([k, v]) => [k, parseFloat(v)])
    );
}

export function calculateEstimatedMonthlyIncome(
    nominalValue: number,
    quantity: number,
    initialInterestRate: number,
): number {
    const totalInvestment = nominalValue * quantity;
    return (totalInvestment * (initialInterestRate / 100)) / 12;
}
