using System;
using __GAME__.Core;
using NUnit.Framework;
using UnityEngine;

namespace __GAME__.Tests.EditMode
{
    /// <summary>
    /// Every ease is picked from a dropdown in the Inspector, so a curve that misbehaves at its
    /// endpoints silently breaks whichever value it shapes. These cover the contract all of them share.
    /// </summary>
    public sealed class EasingTests
    {
        static Ease[] AllEases => (Ease[])Enum.GetValues(typeof(Ease));

        [Test]
        public void EveryEase_PinsBothEndpoints([ValueSource(nameof(AllEases))] Ease ease)
        {
            Assert.AreEqual(0f, Easing.Evaluate(ease, 0f), 1e-4f, ease + " 0 noktasında 0 vermeli");
            Assert.AreEqual(1f, Easing.Evaluate(ease, 1f), 1e-4f, ease + " 1 noktasında 1 vermeli");
        }

        [Test]
        public void EveryEase_ClampsOutOfRangeInput([ValueSource(nameof(AllEases))] Ease ease)
        {
            Assert.AreEqual(0f, Easing.Evaluate(ease, -5f), 1e-4f, ease + " negatif girdiyi kırpmalı");
            Assert.AreEqual(1f, Easing.Evaluate(ease, 5f), 1e-4f, ease + " 1 üstünü kırpmalı");
        }

        [Test]
        public void EveryEase_StaysFinite([ValueSource(nameof(AllEases))] Ease ease)
        {
            for (int i = 0; i <= 20; i++)
            {
                float value = Easing.Evaluate(ease, i / 20f);
                Assert.IsFalse(float.IsNaN(value) || float.IsInfinity(value),
                               ease + " sonlu bir değer vermeli");
            }
        }

        [Test]
        public void SerializedValues_NeverChange()
        {
            // Scenes, prefabs and ScriptableObjects store the number, not the name. A renumbered member
            // silently swaps the curve in every saved tuning, so this table pins every member. A new curve adds
            // one row with its new number; an existing row never changes.
            var pinned = new (string name, int value)[]
            {
                ("Linear", 0),
                ("SineIn", 1), ("SineOut", 2), ("SineInOut", 3),
                ("QuadIn", 4), ("QuadOut", 5), ("QuadInOut", 6),
                ("CubicIn", 7), ("CubicOut", 8), ("CubicInOut", 9),
                ("QuartIn", 10), ("QuartOut", 11),
                ("QuintIn", 12), ("QuintOut", 13),
                ("ExpoIn", 14), ("ExpoOut", 15), ("ExpoInOut", 16),
                ("CircIn", 17), ("CircOut", 18),
                ("BackIn", 19), ("BackOut", 20),
                ("ElasticOut", 21), ("BounceOut", 22),
            };

            Assert.AreEqual(pinned.Length, Enum.GetNames(typeof(Ease)).Length,
                            "Ease üyesi eklendi ya da silindi: tabloya yeni sayısıyla bir satır ekle");
            foreach (var (name, value) in pinned)
            {
                Assert.IsTrue(Enum.IsDefined(typeof(Ease), name), name + " Ease'ten silinmiş ya da adı değişmiş");
                Assert.AreEqual(value, (int)Enum.Parse(typeof(Ease), name), name + " sayısı değişmiş");
            }
        }

        [Test]
        public void SerializedValues_AreUnique()
        {
            // An explicit number copied by mistake would make two names load as the same curve.
            var values = (int[])Enum.GetValues(typeof(Ease));
            var names = Enum.GetNames(typeof(Ease));
            Assert.AreEqual(names.Length, new System.Collections.Generic.HashSet<int>(values).Count,
                            "iki Ease aynı sayıyı paylaşıyor");
        }

        [Test]
        public void Linear_LeavesProgressUntouched()
        {
            // Linear is the "no shaping" option, so anything it changes is a behaviour change for
            // every value that ships with it selected.
            for (int i = 0; i <= 10; i++)
            {
                float t = i / 10f;
                Assert.AreEqual(t, Easing.Evaluate(Ease.Linear, t), 1e-6f, "Linear " + t + " girdisini değiştirmemeli");
            }
        }

        [Test]
        public void InCurves_StartSlow_AndOutCurvesStartFast()
        {
            Assert.Less(Easing.Evaluate(Ease.CubicIn, 0.25f), 0.25f, "In eğrisi başta geride olmalı");
            Assert.Greater(Easing.Evaluate(Ease.CubicOut, 0.25f), 0.25f, "Out eğrisi başta önde olmalı");
        }

        [Test]
        public void BackOut_OvershootsPastOne_ThenSettles()
        {
            float peak = 0f;
            for (int i = 0; i <= 100; i++)
                peak = Mathf.Max(peak, Easing.Evaluate(Ease.BackOut, i / 100f));

            Assert.Greater(peak, 1f, "BackOut hedefi aşıp geri dönmeli");
        }
    }
}
