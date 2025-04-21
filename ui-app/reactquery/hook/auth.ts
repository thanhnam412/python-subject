import { useMutation } from "@tanstack/react-query"
import * as AuthServices from "@/services/auth";
import { useAuth } from "@/hooks/useAuth";


export const useLogin = () => {
  return useMutation({
    mutationFn: AuthServices.postLogin,
    onError: console.log
  })
}

export const useRegister = () => {
  return useMutation({
    mutationFn: AuthServices.postRegister,
    onError: console.log
  })
}


export const useLogout = () => {
  const auth = useAuth()
  return useMutation({
    mutationFn: () => AuthServices.postLogout(auth),
    onError: console.log,
  })
}