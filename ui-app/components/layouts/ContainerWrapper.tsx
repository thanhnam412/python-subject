import { ReactNode } from "react";

interface Props {
  children: ReactNode;
  className?: string;
}

const ContainerWrapper = ({ children, className }: Props) => {
  return (
    <div className={`w-screen bg-[#F4F5F7] min-h-dvh ${className}`}>
      {children}
    </div>
  );
};

export default ContainerWrapper;
