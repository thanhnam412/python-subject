import ContainerWrapper from "@/components/layouts/ContainerWrapper";
import { LoginForm } from "@/components/login-form";
import Image from "next/image";

export default function LoginPage() {
  return (
    <ContainerWrapper className="grid grid-cols-11">
      <LoginForm className="col-span-5 h-full flex flex-col justify-center p-[100px]" />
      <div className="bg-[#A3CFCB] col-span-6 flex flex-col items-center relative">
        <p className="text-[#299D91] font-bold text-[70px] mt-[175px]">
          QUẢN LÝ CHI TIÊU
        </p>
        <div className="absolute w-full bottom-0">
          <div className="relative aspect-[900/600] w-full bg-cover">
            <Image src="/bg-login.png" fill alt="" />
          </div>
        </div>
      </div>
    </ContainerWrapper>
  );
}
