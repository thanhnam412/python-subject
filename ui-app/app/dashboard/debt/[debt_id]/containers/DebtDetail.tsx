"use client";

import { useDebtDetail } from "@/reactquery/hook/debts";
import LoanDetail from "../components/LoanDetail";

interface Props {
  slug: string;
}

function formatNumber(str: string) {
  const digits = str.replace(/\D/g, "");
  return digits ? parseInt(digits, 10) : 0;
}

const DebtDetail = ({ slug }: Props) => {
  const { data: res } = useDebtDetail(formatNumber(slug));
  const { data } = res || {};

  if (!data) return null;

  return <LoanDetail data={data} />;
};

export default DebtDetail;
