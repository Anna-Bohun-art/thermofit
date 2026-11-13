import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { FitResult } from './api'
import { FitChart } from './FitChart.tsx'

//Baut ein minimales FitResult, damit jeder Test nur die Daten angeben muss
function makeResult(x:number[], y:number[]):FitResult {
    return{
        model: 'dsc_two_state', params:[],
        x,y, x_fit:x, y_fit:y,
        residuals: x.map(()=>0),
        r2:1, rmse:0, n_points: x.length, extras:{},
    }
}
describe('FitChart', ()=>{
    it('renders without data', ()=>{
        render(<FitChart result={makeResult([], [])} xLabel="T (°C)"  yLabel="Cp"/>)
        expect(screen.getByRole('img', {name: "Data points and fitted curve"})).toBeTruthy()
        expect(screen.getAllByRole('img', {name: 'Residuals'})).toBeTruthy()
    })
    it('renders with data, including legend and residuals heating', ()=>{
        render(<FitChart result={makeResult([40, 45, 50],[0.1, 2.0, 0.1])} xLabel="T (°C)" yLabel="Cp"/>)
        expect(screen.getByText('data')).toBeTruthy()
        expect(screen.getByText('fit')).toBeTruthy()
        expect(screen.getByRole('heading', { name: 'Residuals' })).toBeTruthy()
    })
})