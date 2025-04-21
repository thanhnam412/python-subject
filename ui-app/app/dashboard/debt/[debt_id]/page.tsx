import DebtDetail from "./containers/DebtDetail";

export default async function Page({
  params,
}: {
  params: Promise<{ debt_id: string }>;
}) {
  const { debt_id } = await params;

  return <DebtDetail slug={debt_id}/>;
}
