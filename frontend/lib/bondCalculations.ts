import { apiFetch } from "./api";

export async function fetchMonthlyIncome(
    bondHolderId: string,
    targetDate?: string,
): Promise<number> {
    let dateToUse = targetDate;
    
    if (!dateToUse) {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, "0");
        dateToUse = `${year}-${month}-01`;
    }
    const result = await apiFetch<string>(
        `/calculations/month-income?bondholder_id=${bondHolderId}&target_date=${dateToUse}`,
        {
            method: "POST",
        },
    );

    return parseFloat(result);
}

export async function fetchTotalMonthlyIncome(
    bondholderIds: string[],
    targetDate?: string,
): Promise<number> {
    if (bondholderIds.length === 0) return 0;

    const incomePromises = bondholderIds.map(async (id) => {
        try {
            return await fetchMonthlyIncome(id, targetDate);
        } catch (error) {
            console.error(
                `Failed to fetch income for bondholder ${id}:`,
                error,
            );
            return 0;
        }
    });

    const incomes = await Promise.all(incomePromises);
    return incomes.reduce((sum, income) => sum + income, 0);
}

export function calculateEstimatedMonthlyIncome(
    nominalValue: number,
    quantity: number,
    initialInterestRate: number,
): number {
    const totalInvestment = nominalValue * quantity;
    return (totalInvestment * (initialInterestRate / 100)) / 12;
}
