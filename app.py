from flask import Flask, request, jsonify
from playwright.async_api import async_playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
import asyncio
import json
#import sv

import logging

app = Flask(__name__)

# playwright injection system
############################################
maths_table_ig = ['=', '-', '/', '*', '+', '%', '**', '//']

cool_table = {
    'infinity': '∞',
    'pi': 'π',
    'e': 'e',
    'i': 'i',
    'phi': 'φ',
    'omega': 'ω',
    'alpha': 'α',
    'beta': 'β',
    'delta': 'δ',
    'eta': 'η',
    'theta': 'θ',
    'lambda': 'λ',
    'pi': 'π',
    'rho': 'ρ',
    
    'approaches': '→',
    'equals': '==',
    'equal': '==',
    'less than': '<',
    'greater than': '>',

    'multipl': '*',
    'divid': '/',
    'add': '+',
    'subtract': '-',
    'modulus': 'mod',
    'factorial': '!',
    'root': '√',

    'simplified': 'simplf',
    'indeterminate': 'indet',
    'undefined': 'undef',
    'identify': 'ident',
    'determine': 'dterm',
    'constant': 'const',
    'variable': 'var',
    'function': 'func',
    'derivative': 'deriv',
    'integral': 'int',
    'summation': 'sum',
    'product': 'prod',
    'limit': 'lim',
    'sequence': 'seq',
    'vertical': 'vert',
    'horizontal': 'horiz',
    'matrix': 'mtrx',
    'expression': 'expr',
    'equation': 'eq',
    'inequality': 'ineq',
    'logarithm': 'log',
    'degree': 'degº',
    'radian': 'rad',
    'numerator': 'numertr',
    'denominator': 'dnomintr',
    'evaluate': 'eval',
    'simplify': 'simplf',
    'calculate': 'calc',
    'coefficient': 'coeff',
    'previous': 'prev',
    'approximately': 'approx',
    'approximate': 'approx',
    'element': 'elem',
    


    'the ': '',
}

import re
def Lower(s):
    return re.sub(r'^(\S)', lambda m: m.group(1).lower(), s)

async def get_response(query):
    async with async_playwright() as p:
        print("launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://web.szl.ai/problem")
        await page.wait_for_load_state("networkidle")
        print("browser online, network status: idle")
        print("[Interact] Query:", query)
        await page.type("body", query)
        
        print('[Interact] Submitting form')
        button = await page.query_selector(".flex.flex-row.items-center.ml-2 svg[data-testid='SendRoundedIcon']")
        await button.click()

        original_url = page.url
        try:
            async with page.expect_navigation(timeout=2500, wait_until="domcontentloaded"):
                pass
            print("Navigation successful; proceeding with page.url:", page.url)
        except PlaywrightTimeoutError:
            print("Timed out waiting for navigation")
            await browser.close()
            return json.dumps({'error': 'Navigation timed out || Not enough information provided'})

        if page.url != original_url:
            print("Page refreshed, waiting for it to stabilize")
            print("Page URL:", page.url)
        else:
            print("No navigation detected")
            await browser.close()
            return json.dumps({'error': 'Failed to reload page || Not enough information provided'})
        
        await page.wait_for_selector('div.flex.m-\\[27px\\]')
        
        while True:
            try:
                print('[Interact] Clicking new reveal step')
                await page.click('div.flex.m-\\[27px\\] button:has-text("Reveal step")', timeout=2500)
            except:
                break
        
        print('Done revealing steps')
        
        all_elements = await page.query_selector_all('div.undefined.relative')
        
        steps = {}
        for i, element in enumerate(all_elements):
            is_inside_bold = await element.evaluate('''
                (element) => {
                    while (element) {
                        if (element.matches('div.font-bold')) return true;
                        element = element.parentElement;
                    }
                    return false;
                }
            ''')
            
            if not is_inside_bold:
                content = await element.text_content()
                step_content = await all_elements[i-1].text_content()
                steps[Lower(step_content)] = Lower(content)
        
        print("Processing steps...")
        processed_steps = {}
        for step, content in steps.items():
            if set(step + content) & set(maths_table_ig):
                for key, value in cool_table.items():
                    step = step.replace(key, value)
                    content = content.replace(key, value)
            processed_steps[step] = content
        
        await browser.close()
        print("browser terminated, success")
        return json.dumps(processed_steps, indent=2)
############################################
@app.route('/')
def hello_world():
    return 'hello :^)'

@app.route('/request', methods=['POST'])
def create_user():
    user_data = request.get_json()
    logging.info(user_data['input'])
    response = asyncio.run(get_response(query=user_data['input']))
    return jsonify(response), 201

if __name__ == "__main__":
    app.run()
