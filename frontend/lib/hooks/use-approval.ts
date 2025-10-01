"use client"

import { useMutation, useQuery } from "@tanstack/react-query"
import { approvalsApi } from "../api-client"
import type { ApprovalDecision } from "../types"

export function useApprovalDetails(token: string) {
  return useQuery({
    queryKey: ["approval", token],
    queryFn: () => approvalsApi.getDetails(token),
    retry: false,
    staleTime: 0,
  })
}

export function useSubmitApproval(token: string) {
  return useMutation({
    mutationFn: (decision: ApprovalDecision) => approvalsApi.submit(token, decision),
    onSuccess: () => {
      // Invalidate the approval query to refetch the status
      // This would typically use queryClient.invalidateQueries()
      // but we'll handle it in the component for simplicity
    },
  })
}
