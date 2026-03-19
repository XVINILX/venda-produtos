# backend/src/services/coupon_service.py
from typing import Dict, List, Optional
from fastapi import HTTPException, status
from src.repositories.coupon_repository import CouponRepository
from src.schemas.coupon_schemas import CouponCreate, CouponUpdate
from datetime import datetime

class CouponService:
    def __init__(self):
        self.coupon_repo = CouponRepository()
    
    def _validate_coupon_data(self, coupon_data: Dict, is_update: bool = False):
        """Valida dados do cupom"""
        if not is_update:
            # Validações para criação
            if not coupon_data.get('code'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código do cupom é obrigatório"
                )
            
            if len(coupon_data['code']) < 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código do cupom deve ter pelo menos 3 caracteres"
                )
        
        # Validações comuns
        if 'discount_type' in coupon_data:
            if coupon_data['discount_type'] not in ['percentage', 'fixed']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tipo de desconto deve ser 'percentage' ou 'fixed'"
                )
        
        if 'discount_value' in coupon_data:
            if coupon_data['discount_value'] <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Valor do desconto deve ser maior que zero"
                )
            
            if coupon_data.get('discount_type') == 'percentage' and coupon_data['discount_value'] > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Desconto percentual não pode ser maior que 100%"
                )
        
        if 'expires_at' in coupon_data:
            if coupon_data['expires_at'] <= datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Data de expiração deve ser no futuro"
                )
    
    def create_coupon(self, coupon_data: CouponCreate) -> Dict:
        """Cria um novo cupom"""
        data = coupon_data.dict()
        
        # Validar dados
        self._validate_coupon_data(data)
        
        # Verificar se código já existe
        if self.coupon_repo.coupon_exists(data['code']):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Já existe um cupom com o código {data['code']}"
            )
        
        # Criar cupom
        return self.coupon_repo.create_coupon(data)
    
    def get_coupon(self, coupon_id: int) -> Dict:
        """Busca um cupom por ID"""
        coupon = self.coupon_repo.get_coupon_by_id(coupon_id)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cupom não encontrado"
            )
        return coupon
    
    def get_coupon_by_code(self, code: str) -> Dict:
        """Busca um cupom por código"""
        coupon = self.coupon_repo.get_coupon_by_code(code)
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cupom não encontrado"
            )
        return coupon
    
    def get_all_coupons(self) -> List[Dict]:
        """Lista todos os cupons"""
        return self.coupon_repo.get_all_coupons()
    
    def get_active_coupons(self) -> List[Dict]:
        """Lista cupons ativos"""
        return self.coupon_repo.get_active_coupons()
    
    def get_expired_coupons(self) -> List[Dict]:
        """Lista cupons expirados"""
        return self.coupon_repo.get_expired_coupons()
    
    def update_coupon(self, coupon_id: int, update_data: CouponUpdate) -> Dict:
        """Atualiza um cupom"""
        # Verificar se existe
        existing = self.get_coupon(coupon_id)
        
        data = update_data.dict(exclude_unset=True)
        
        # Validar dados
        self._validate_coupon_data(data, is_update=True)
        
        # Se estiver mudando o código, verificar se novo código já existe
        if 'code' in data and data['code'] != existing['code']:
            if self.coupon_repo.coupon_exists(data['code']):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Já existe um cupom com o código {data['code']}"
                )
        
        # Atualizar
        updated = self.coupon_repo.update_coupon(coupon_id, data)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cupom não encontrado"
            )
        
        return updated
    
    def delete_coupon(self, coupon_id: int) -> bool:
        """Remove um cupom"""
        # Verificar se existe
        self.get_coupon(coupon_id)
        
        if not self.coupon_repo.delete_coupon(coupon_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cupom não encontrado"
            )
        
        return True
    
    def activate_coupon(self, coupon_id: int) -> Dict:
        """Ativa um cupom"""
        coupon = self.get_coupon(coupon_id)
        
        if coupon['active']:
            return coupon  # Já está ativo
        
        return self.coupon_repo.activate_coupon(coupon_id)
    
    def deactivate_coupon(self, coupon_id: int) -> Dict:
        """Desativa um cupom"""
        coupon = self.get_coupon(coupon_id)
        
        if not coupon['active']:
            return coupon  # Já está inativo
        
        return self.coupon_repo.deactivate_coupon(coupon_id)
    
    def get_coupon_stats(self) -> Dict:
        """Retorna estatísticas dos cupons"""
        return self.coupon_repo.get_coupon_stats()
    
    def validate_coupon(self, code: str) -> Dict:
        """Valida se um cupom é válido para uso"""
        coupon = self.coupon_repo.get_valid_coupon(code)
        
        if not coupon:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cupom inválido ou expirado"
            )
        
        return coupon